import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
import sqlite3

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA

from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Portfolio AI Chatbot",
    description="A RAG-based AI chatbot providing information about the user's portfolio.",
    version="1.0.0"
)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for the RAG chain
qa_chain = None

# Custom Prompt Template for Saad's Portfolio
template = """You are Saad Ali Hamid's Personal AI Portfolio Assistant. 
You are friendly, professional, and very knowledgeable about Saad's background, projects, and skills.
Saad is a Python Developer and AI Automation Specialist. 

Important Details to remember:
- Saad is currently working at Tkxel as an AI Automation Developer.
- He is studying at Muhammad Nawaz Sharif University of Engineering and Technology (MNS-UET), Multan (BSCS 8th Semester).
- He won the Shahbaz Sharif Laptop Award.

Use the following context to answer the user's question. 
If the user asks in Roman Urdu (e.g., "saad ki uni kya hai"), respond in the same friendly Roman Urdu.
If the context doesn't have the answer, politely say that Saad hasn't shared that detail yet, but mention his current role at Tkxel.

Context: {context}
Question: {question}
Answer:"""

PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])

@app.on_event("startup")
async def startup_event():
    global qa_chain
    print("Initializing RAG application components...")
    
    # Validate API Key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("Warning: GROQ_API_KEY environment variable is not set. Requests will fail if not provided.")

    persist_directory = "saad_db"
    
    if not os.path.exists(persist_directory):
        print(f"Warning: persist_directory '{persist_directory}' not found. Did you run ingest.py?")

    # Match the embeddings model used in ingest.py
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Load ChromaDB from disk
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    
    # Initialize the Groq LLM
    llm = ChatGroq(
        api_key=groq_api_key,
        temperature=0.2, 
        model_name="llama-3.3-70b-versatile"
    )
    
    # Create the RetrievalQA chain with custom prompt
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=False
    )
    
    print("RAG components initialized successfully with custom prompt.")
    
    print("RAG components initialized successfully.")
    
    # Initialize leads database
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL)")
    conn.commit()
    conn.close()
    print("Leads database initialized.")

# Route models
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str

class EmailRequest(BaseModel):
    email: str

@app.post("/save-email")
async def save_email(request: EmailRequest):
    try:
        conn = sqlite3.connect('leads.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO leads (email) VALUES (?)", (request.email,))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Email saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not qa_chain:
        raise HTTPException(status_code=500, detail="Chatbot components are not fully initialized.")
    
    try:
        # Run the query through the chain
        result = qa_chain.invoke({"query": request.query})
        answer = result.get("result", "I'm sorry, I couldn't generate an answer.")
        
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "API is running."}

if __name__ == "__main__":
    import uvicorn
    print("Starting uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
