from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from app.core.audio_pipeline import (
    AudioPipelineError,
    process_audio,
)
from app.core.curly import Curly
from app.stt.service import STTService


def create_process_router(
    curly: Curly,
    stt: STTService,
):
    router = APIRouter()

    @router.post("/v1/process")
    async def process_audio_endpoint(
        session_id: str = Form(...),
        file: UploadFile = File(...),
        context: str | None = Form(None),
    ):
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_AUDIO",
                    "message": "Audio file is required.",
                },
            )

        try:
            content = await file.read()

            result = await process_audio(
                curly=curly,
                stt=stt,
                session_id=session_id,
                content=content,
                filename=file.filename,
                context=context,
            )

            return {
                "session_id": session_id,
                "transcript": {
                    "text": result.text,
                    "language": result.transcription.get(
                        "language",
                        "",
                    ),
                    "language_probability": result.transcription.get(
                        "language_probability",
                        0.0,
                    ),
                },
                "response": result.curly_response.model_dump(),
                "latency_ms": {
                    "stt": round(
                        result.stt_latency_ms,
                        2,
                    ),
                    "curly": round(
                        result.curly_latency_ms,
                        2,
                    ),
                    "total": round(
                        result.stt_latency_ms
                        + result.curly_latency_ms,
                        2,
                    ),
                },
            }

        except AudioPipelineError as error:
            raise HTTPException(
                status_code=error.status_code,
                detail={
                    "code": error.code,
                    "message": error.message,
                },
            ) from error

    return router