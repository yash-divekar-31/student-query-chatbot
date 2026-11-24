from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return a minimal status response for service monitoring."""
    return {
        "status": "ok",
        "service": "student-query-chatbot",
    }
