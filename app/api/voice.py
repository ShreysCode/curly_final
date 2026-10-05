import os

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse

from app.core.audio_pipeline import (
    AudioPipelineError,
    process_audio,
)
from app.core.curly import Curly, CurlyState
from app.stt.service import STTService
from app.tts.service import TTSService


def create_voice_router(
    curly: Curly,
    stt: STTService,
    tts: TTSService,
):
    router = APIRouter()

    @router.post("/v1/voice")
    async def voice(
        session_id: str = Form(...),
        file: UploadFile = File(...),
        context: str | None = Form(None),
    ):

        # ====================================================
        # VOICE ENDPOINT DIAGNOSTIC
        # ====================================================

        print()
        print("========== VOICE ENDPOINT REACHED ==========")

        print(
            "Session ID:",
            session_id,
        )

        print(
            "Filename:",
            file.filename,
        )

        print(
            "Content Type:",
            file.content_type,
        )

        print(
            "Context:",
            context,
        )

        print("=============================================")
        print()

        # ====================================================
        # VALIDATE AUDIO FILE
        # ====================================================

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_AUDIO",
                    "message": "Audio file is required.",
                },
            )

        try:

            # =================================================
            # READ AUDIO
            # =================================================

            content = await file.read()

            print(
                "Voice audio bytes:",
                len(content),
            )

            # =================================================
            # PROCESS AUDIO
            # =================================================

            result = await process_audio(
                curly=curly,
                stt=stt,
                session_id=session_id,
                content=content,
                filename=file.filename,
                context=context,
            )

            print()
            print("========== VOICE PROCESSING COMPLETE ==========")

            print(
                "Transcript:",
                result.text,
            )

            print(
                "Curly response:",
                result.curly_response.text,
            )

            print(
                "Curly type:",
                result.curly_response.type.value,
            )

            print(
                "Curly command:",
                result.curly_response.command.name,
            )

            print(
                "Curly state:",
                result.curly_response.state.value,
            )

            print("===============================================")
            print()

            # =================================================
            # VALIDATE CURLY RESPONSE
            # =================================================

            if not result.curly_response.text:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "code": "EMPTY_RESPONSE",
                        "message": (
                            "Curly produced no spoken response."
                        ),
                    },
                )

            # =================================================
            # SET CURLY STATE
            # =================================================

            curly.set_state(
                session_id,
                CurlyState.SPEAKING,
            )

            # =================================================
            # TEXT TO SPEECH
            # =================================================

            try:

                audio_path = await tts.synthesize(
                    result.curly_response.text
                )

                print(
                    "TTS audio path:",
                    audio_path,
                )

            except Exception as error:

                curly.set_state(
                    session_id,
                    CurlyState.ERROR,
                )

                print(
                    "TTS ERROR:",
                    repr(error),
                )

                raise HTTPException(
                    status_code=500,
                    detail={
                        "code": "TTS_FAILED",
                        "message": (
                            "Speech generation failed."
                        ),
                    },
                ) from error

            # =================================================
            # RETURN AUDIO RESPONSE
            # =================================================

            return FileResponse(
                path=audio_path,
                media_type="audio/mpeg",
                filename=audio_path.name,
                headers={
                    "X-Curly-Session-Id": session_id,

                    "X-Curly-Transcript": (
                        result.text
                    ),

                    "X-Curly-Type": (
                        result.curly_response.type.value
                    ),

                    "X-Curly-Command": (
                        result.curly_response.command.name
                    ),

                    "X-Curly-State": (
                        result.curly_response.state.value
                    ),
                },
            )

        # ====================================================
        # AUDIO PIPELINE ERROR
        # ====================================================

        except AudioPipelineError as error:

            print()
            print("========== AUDIO PIPELINE ERROR ==========")

            print(
                "Status:",
                error.status_code,
            )

            print(
                "Code:",
                error.code,
            )

            print(
                "Message:",
                error.message,
            )

            print("==========================================")
            print()

            raise HTTPException(
                status_code=error.status_code,
                detail={
                    "code": error.code,
                    "message": error.message,
                },
            ) from error

        # ====================================================
        # EXISTING HTTP ERROR
        # ====================================================

        except HTTPException:

            raise

        # ====================================================
        # UNEXPECTED ERROR
        # ====================================================

        except Exception as error:

            print()
            print("========== VOICE PROCESSING ERROR ==========")

            print(
                "Error type:",
                type(error),
            )

            print(
                "Error:",
                repr(error),
            )

            print("============================================")
            print()

            curly.set_state(
                session_id,
                CurlyState.ERROR,
            )

            raise HTTPException(
                status_code=500,
                detail={
                    "code": "VOICE_PROCESSING_FAILED",
                    "message": (
                        "Voice processing failed."
                    ),
                },
            ) from error

    return router