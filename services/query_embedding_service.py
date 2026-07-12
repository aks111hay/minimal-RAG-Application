from models.input_schema import QueryInput
from typing import Dict
from utils.generate_embedding_utils import get_embedding
from config import collection,ai_client,faq_collection
from fastapi import HTTPException
from config import ai_client
from google.genai import types
from models.query_schema import QueryInputPayload

def generate_answer(question:QueryInput) -> Dict[str,str]:

    collected_questions = []


    vector = get_embedding(question.question)

    faq_result = faq_collection.query(
        query_embeddings=[vector],
        n_results=2,
        include=["documents","distances","metadatas"]
    )

    faq_distances = faq_result.get("distances",[[]])[0]
    if faq_distances and faq_distances[0]<0.5:
        faq_answer = faq_result.get("documents")[0][0]
        original_faq = faq_result.get("metadatas")[0][0].get("original_question","matched faq")

    faq_prompt = f"""you are a polite customer support assistant.answer the user's question using the only provided official policy text.Do not invent details .keep it conversational but strictly accurate to the policy.
    official policy text : {faq_answer}

    user's question :{question.question}
    """

    response = ai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=faq_prompt
    )



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



def decompose_user_query(orginal_query : str) -> QueryInputPayload:
    decomposition_prompt = 
