import os
import sys

# Add the app directory to the path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)
os.chdir(app_dir)

from chatbot import app

# Passenger expects the ASGI/WSGI app to be named 'application'
# For FastAPI (ASGI), we need an adapter
try:
    from a2wsgi import ASGIMiddleware
    application = ASGIMiddleware(app)
except ImportError:
    # Fallback: use uvicorn as ASGI server
    import asyncio
    from uvicorn.middleware.wsgi import WSGIMiddleware

    class SimpleWSGIAdapter:
        def __init__(self, asgi_app):
            self.asgi_app = asgi_app

        def __call__(self, environ, start_response):
            import io
            from urllib.parse import unquote

            path = environ.get('PATH_INFO', '/')
            method = environ.get('REQUEST_METHOD', 'GET')
            query_string = environ.get('QUERY_STRING', '').encode('utf-8')

            headers = []
            for key, value in environ.items():
                if key.startswith('HTTP_'):
                    header_name = key[5:].replace('_', '-').lower()
                    headers.append([header_name.encode(), value.encode()])
                elif key == 'CONTENT_TYPE':
                    headers.append([b'content-type', value.encode()])
                elif key == 'CONTENT_LENGTH':
                    headers.append([b'content-length', value.encode()])

            body = environ.get('wsgi.input', io.BytesIO(b'')).read()

            scope = {
                'type': 'http',
                'asgi': {'version': '3.0'},
                'http_version': '1.1',
                'method': method,
                'path': unquote(path),
                'query_string': query_string,
                'headers': headers,
                'server': (environ.get('SERVER_NAME', 'localhost'), int(environ.get('SERVER_PORT', '80'))),
            }

            loop = asyncio.new_event_loop()
            status_code = None
            response_headers = None
            response_body = []

            async def receive():
                return {'type': 'http.request', 'body': body}

            async def send(message):
                nonlocal status_code, response_headers
                if message['type'] == 'http.response.start':
                    status_code = message['status']
                    response_headers = message.get('headers', [])
                elif message['type'] == 'http.response.body':
                    response_body.append(message.get('body', b''))

            try:
                loop.run_until_complete(self.asgi_app(scope, receive, send))
            finally:
                loop.close()

            status_map = {200: 'OK', 201: 'Created', 204: 'No Content', 301: 'Moved', 302: 'Found',
                          400: 'Bad Request', 404: 'Not Found', 405: 'Method Not Allowed', 500: 'Internal Server Error', 422: 'Unprocessable Entity'}
            status_text = f"{status_code} {status_map.get(status_code, 'Unknown')}"
            wsgi_headers = [(h[0].decode() if isinstance(h[0], bytes) else h[0],
                             h[1].decode() if isinstance(h[1], bytes) else h[1]) for h in (response_headers or [])]

            start_response(status_text, wsgi_headers)
            return response_body

    application = SimpleWSGIAdapter(app)
