import logging

from fastapi import APIRouter, Request


router = APIRouter(
    prefix="/voice",
    tags=["Voice Agent"]
)

logger = logging.getLogger(__name__)


@router.get("/health")
def voice_health():

    return {
        "data": {
            "voice_agent": "online"
        },
        "error": None,
    }


@router.post("/webhook")
async def voice_webhook(
    request: Request
):

    try:

        payload = await request.json()

        logger.info(
            "VOICE_WEBHOOK payload=%s",
            payload
        )

        return {
            "data": {
                "received": True
            },
            "error": None,
        }

    except Exception as exc:

        logger.exception(
            "Voice webhook error"
        )

        return {
            "data": None,
            "error": str(exc),
        }