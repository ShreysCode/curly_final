import json
import os
import tempfile
import time
from dataclasses import dataclass

from app.core.curly import Curly
from app.models.schemas import CurlyState
from app.stt.service import STTService

ALLOWED_AUDIO_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".ogg",
    ".webm",
}


MAX_AUDIO_BYTES = 10 * 1024 * 1024


@dataclass
class AudioPipelineResult:
    text: str
    transcription: dict
    curly_response: object
    stt_latency_ms: float
    curly_latency_ms: float


class AudioPipelineError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def process_audio(
    curly: Curly,
    stt: STTService,
    session_id: str,
    content: bytes,
    filename: str,
    context: str | None = None,
) -> AudioPipelineResult:

    if session_id not in curly.sessions:
        raise AudioPipelineError(
            "INVALID_SESSION",
            "Session not found.",
            404,
        )

    if not content:
        raise AudioPipelineError(
            "EMPTY_AUDIO",
            "Audio file is empty.",
            400,
        )

    if len(content) > MAX_AUDIO_BYTES:
        raise AudioPipelineError(
            "AUDIO_TOO_LARGE",
            "Audio file exceeds the 10 MB limit.",
            413,
        )

    suffix = os.path.splitext(filename)[1].lower()

    if suffix not in ALLOWED_AUDIO_EXTENSIONS:
        raise AudioPipelineError(
            "UNSUPPORTED_AUDIO_FORMAT",
            "Unsupported audio format.",
            415,
        )

    environment_context = {}

    if context:
        try:
            environment_context = json.loads(context)
        except json.JSONDecodeError as error:
            raise AudioPipelineError(
                "INVALID_CONTEXT",
                "Context must be valid JSON.",
                400,
            ) from error

        if not isinstance(environment_context, dict):
            raise AudioPipelineError(
                "INVALID_CONTEXT",
                "Context must be a JSON object.",
                400,
            )
        
    temp_path = None

    try:
        curly.set_state(
            session_id,
            CurlyState.PROCESSING,
        )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp:
            temp_path = temp.name
            temp.write(content)

        stt_start = time.perf_counter()

        try:
            transcription = stt.transcribe(temp_path)
        except ValueError as error:
            curly.set_state(
                session_id,
                CurlyState.LISTENING,
            )
            raise AudioPipelineError(
                "ENGLISH_ONLY",
                "Please speak in English.",
                422,
            ) from error
        except Exception as error:
            curly.set_state(
                session_id,
                CurlyState.ERROR,
            )
            raise AudioPipelineError(
                "STT_FAILED",
                "Speech recognition failed.",
                500,
            ) from error

        stt_latency_ms = (
            time.perf_counter() - stt_start
        ) * 1000

        text = transcription.get(
            "text",
            "",
        ).strip()

        if not text:
            curly.set_state(
                session_id,
                CurlyState.LISTENING,
            )
            raise AudioPipelineError(
                "NO_SPEECH",
                "No speech was detected.",
                422,
            )

        curly_start = time.perf_counter()

        try:
            curly_response = await curly.chat(
                session_id=session_id,
                text=text,
                context=environment_context,
            )
        except Exception as error:
            curly.set_state(
                session_id,
                CurlyState.ERROR,
            )
            raise AudioPipelineError(
                "CURLY_PROCESSING_FAILED",
                "Curly could not process the request.",
                500,
            ) from error

        curly_latency_ms = (
            time.perf_counter() - curly_start
        ) * 1000

        return AudioPipelineResult(
            text=text,
            transcription=transcription,
            curly_response=curly_response,
            stt_latency_ms=stt_latency_ms,
            curly_latency_ms=curly_latency_ms,
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass