import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Minimal Gemini RAG API")

# Initialize the official Google GenAI Client
# It automatically reads GEMINI_API_KEY from the environment
ai_client = genai.Client()

# Initialize ChromaDB locally (persisted in a directory named 'chroma_db')
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="rag_collection")

# --- Pydantic Schemas ---
class DocumentInput(BaseModel):
    id: str
    text: str

class QueryInput(BaseModel):
    question: str

# --- Helper Functions ---
def get_embedding(text: str) -> list[float]:
    """Generates text embedding using Google's embedding model."""
    try:
        result = ai_client.models.embed_content(
            model="gemini-embedding-001",
            contents=text
        )
        # The SDK returns an object with an embedding list containing values
        return result.embeddings[0].values
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")

# --- FastAPI Endpoints ---

@app.post("/embed")
def embed_document(doc: DocumentInput):
    """
    Endpoint to process text, create an embedding, and save it to ChromaDB.
    """
    vector = get_embedding(doc.text)
    
    # Store into ChromaDB
    collection.add(
        ids=[doc.id],
        embeddings=[vector],
        documents=[doc.text]
    )
    return {"status": "success", "message": f"Document '{doc.id}' successfully embedded and stored."}

@app.post("/query")
def query_rag(input_data: QueryInput):
    """
    Endpoint to retrieve matching documentation chunks and ask Gemini for the answer.
    """
    # 1. Embed the user question
    query_vector = get_embedding(input_data.question)
    
    # 2. Search ChromaDB for the top 2 closest context documents
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=2
    )
    
    # Check if we have any retrieved context
    retrieved_docs = results.get("documents", [[]])[0]
    if not retrieved_docs:
        context = "No relevant context found in the database."
    else:
        context = "\n\n".join(retrieved_docs)
    
    # 3. Construct the RAG Prompt
    rag_prompt = f"""
    You are a helpful assistant. Answer the question based ONLY on the provided context. 
    If the context doesn't contain the answer, say "I cannot find the answer in the provided documents."

    Context:
    {context}

    Question: {input_data.question}
    Answer:
    """
    
    # 4. Generate Answer using Gemini 2.5 Flash
    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=rag_prompt,
        )
        return {
            "answer": response.text,
            "retrieved_context": retrieved_docs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini Generation error: {str(e)}")