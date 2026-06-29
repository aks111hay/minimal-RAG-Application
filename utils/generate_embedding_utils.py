from config import ai_client
from fastapi import HTTPException

def get_embedding(text : str) -> list[float]:
    try:
        result = ai_client.models.embed_content(
            model= "gemini-embedding-001",
            contents = text
        )
        return result.embeddings[0].values
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Embedding error : {str(e)}")
    