import logging

from fastapi import APIRouter

from backend.models.schemas import HistoryResponse, QueryInput, QueryResponse
from backend.services import memory_service, query_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1", tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query_rag(payload: QueryInput):
    logger.info("Received /query request for session='%s'", payload.session_id)
    return query_service.answer_question(payload)


@router.get("/history/{session_id}", response_model=HistoryResponse)
def get_history(session_id: str):
    messages = memory_service.get_history(session_id)
    return HistoryResponse(session_id=session_id, messages=messages)


@router.delete("/history/{session_id}")
def clear_history(session_id: str):
    memory_service.clear_history(session_id)
    return {"status": "success", "message": f"History cleared for session '{session_id}'"}