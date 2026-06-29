from google import genai
import chromadb
from dotenv import load_dotenv

load_dotenv()

ai_client = genai.Client()
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="rag_collection")