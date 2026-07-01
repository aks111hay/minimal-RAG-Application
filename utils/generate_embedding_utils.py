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
    

def split_text_into_chunks(text:str,chunk_size:int=1000,chunk_overlap:str=20)->list[str]:
    chunks=[]
    start=0
    text_len=len(text)

    while start<text_len:
        end=start+chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start+=(chunk_size-chunk_overlap)
    return chunks 
    