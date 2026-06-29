from models.input_schema import DocumentInput
from utils.generate_embedding_utils import get_embedding
from config import collection
from typing import Dict

def generate_embedding(doc:DocumentInput)-> Dict[str,str]:
    vector = get_embedding(doc.text)
    collection.add(ids=[doc.id],
                   embeddings=[vector],
                   documents=[doc.text]
                   )
    return {"status":"success","message":f"document {doc.id} successfully embedded"}


