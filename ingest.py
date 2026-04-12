import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def main():
    print("Starting ingestion process...")
    
    # 1. Load the document
    text_file_path = "bio_data.txt"
    if not os.path.exists(text_file_path):
        print(f"Error: {text_file_path} not found.")
        return

    loader = TextLoader(text_file_path)
    documents = loader.load()
    
    # 2. Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100
    )
    docs = text_splitter.split_documents(documents)
    print(f"Split document into {len(docs)} chunks.")
    
    # 3. Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 4. Create and save the vector store
    persist_directory = "saad_db"
    
    # Create the vector store. This processes the chunks and saves them in `saad_db`
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    print("Ingestion completed successfully. Vector database saved to 'saad_db'.")

if __name__ == "__main__":
    main()