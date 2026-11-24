"""Chat endpoint request and response schemas."""

import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.nlp.preprocessing import normalize_text
from app.services.chatbot_service import ChatbotService


logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1, max_length=500)

    @field_validator("question")
    @classmethod
    def question_must_contain_searchable_text(cls, value: str) -> str:
        if not normalize_text(value):
            raise ValueError("question must contain letters or numbers.")
        return value.strip()


class ChatResponse(BaseModel):
    success: bool
    question: str
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    response: str
    is_fallback: bool


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    """Classify a student question and return its dataset-backed response."""
    chatbot_service: ChatbotService | None = getattr(
        request.app.state,
        "chatbot_service",
        None,
    )
    if chatbot_service is None:
        raise HTTPException(
            status_code=503,
            detail="The chatbot is temporarily unavailable. Please try again later.",
        )

    try:
        answer = chatbot_service.answer(payload.question)
    except (RuntimeError, ValueError) as error:
        logger.exception("Chat request processing failed")
        raise HTTPException(
            status_code=500,
            detail="The chatbot could not process this request.",
        ) from error

    return ChatResponse(
        success=True,
        question=payload.question,
        intent=answer.intent,
        confidence=answer.confidence,
        response=answer.response,
        is_fallback=answer.is_fallback,
    )
