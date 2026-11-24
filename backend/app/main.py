import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.core.config import settings
from app.services.chatbot_service import (
    ChatbotInitializationError,
    ChatbotService,
)


logger = logging.getLogger(__name__)


def create_app(
    *,
    model_dir: Path = settings.model_dir,
    dataset_path: Path = settings.dataset_path,
    confidence_threshold: float = settings.confidence_threshold,
) -> FastAPI:
    """Create the application and initialize chatbot resources once per lifespan."""

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        try:
            application.state.chatbot_service = ChatbotService.from_files(
                model_dir=model_dir,
                dataset_path=dataset_path,
                confidence_threshold=confidence_threshold,
            )
        except ChatbotInitializationError as error:
            logger.error("Chatbot initialization failed: %s", error)
            application.state.chatbot_service = None

        yield
        application.state.chatbot_service = None

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    application.include_router(health_router)
    application.include_router(chat_router)
    return application


app = create_app()
