from models.input_schema import QueryInput
from typing import Dict
from utils.generate_embedding_utils import get_embedding
from config import collection,ai_client
from fastapi import HTTPException

def generate_answer(question:QueryInput) -> Dict[str,str]:
    vector = get_embedding(question.question)

    result = collection.query(
        query_embeddings=[vector],
        n_results=2
    )

    retrieved_docs = result.get("documents",[[]])[0]
    if not retrieved_docs:
        context = "No relevant information found in document"
    else:
        context="/n/n".join(retrieved_docs)

    rag_prompt = f"""
    You are a helpful assistant. Answer the question based ONLY on the provided context. 
    If the context doesn't contain the answer, say "I cannot find the answer in the provided documents."

    Context:
    {context}

    Question: {question.question}
    Answer:
    """

    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=rag_prompt
        )

        return {
            "answer":response.text,
            "retrieved_docs":retrieved_docs
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Gemini Generation error: {str(e)}")

