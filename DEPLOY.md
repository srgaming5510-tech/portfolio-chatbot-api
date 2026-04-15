# Deployment Guide — Saad Portfolio Chatbot

## Deploy to Render (Free Hosting)

### Step 1: Push to GitHub
1. Go to https://github.com/new and create a new repository (e.g. `portfolio-chatbot`)
2. Open terminal in the `chat_bot_portfolio` project folder and run:
   ```
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/portfolio-chatbot.git
   git push -u origin main
   ```

### Step 2: Deploy on Render
1. Go to https://render.com and sign up (free) using your GitHub account
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo (`portfolio-chatbot`)
4. Configure:
   - **Name**: `saad-portfolio-chatbot`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn chatbot:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
5. Under **Environment Variables**, add:
   - Key: `GROQ_API_KEY` → Value: your Groq API key (get from https://console.groq.com)
6. Click **"Create Web Service"**

### Step 3: Wait for Build
- Render will install dependencies and start your app
- Once deployed, you'll get a URL like: `https://saad-portfolio-chatbot.onrender.com`
- Visit that URL — your portfolio + chatbot will be live!

## Important Notes
- **Do NOT push your `.env` file** — it contains your secret API key. The `.gitignore` already excludes it.
- The `saad_db/` folder (ChromaDB) MUST be committed to Git so it's available on the server.
- Free Render instances spin down after 15 min of inactivity. First visit after idle may take ~30 seconds.
- To keep it always on, upgrade to Render's paid plan ($7/month).

## Alternative: Deploy to Railway
1. Go to https://railway.app and sign up
2. Click "New Project" → "Deploy from GitHub Repo"
3. Select your repository
4. Add environment variable: `GROQ_API_KEY`
5. Railway auto-detects the Procfile and deploys

## Test Locally Before Deploying
```bash
cd chat_bot_portfolio
pip install -r requirements.txt
python chatbot.py
```
Open http://localhost:8000 in your browser.
