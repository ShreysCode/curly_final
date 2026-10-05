from contextlib import asynccontextmanager

from pathlib import Path


from fastapi import FastAPI


from app.api.chat import create_chat_router

from app.api.process import create_process_router

from app.api.session import create_session_router

from app.api.stt import create_stt_router

from app.api.tts import create_tts_router

from app.api.voice import create_voice_router


from app.config import settings

from app.core.curly import Curly


from app.knowledge.knowledge import KnowledgeBase

from app.llm.ollama import OllamaClient


from app.stt.service import STTService

from app.tts.service import TTSService


from app.core.logging import configure_logging

from app.core.middleware import request_id_middleware

# ============================================================
# LOCAL NETWORK DISCOVERY
# ============================================================

from app.network import CurlyServiceDiscovery


# ============================================================
# LOGGING
# ============================================================

configure_logging()


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# CREATE CURLY SERVICES
# ============================================================

print("Loading Curly services...")


knowledge = KnowledgeBase(
    BASE_DIR / "knowledge" / "data.json"
)


llm = OllamaClient(
    base_url=settings.ollama_url,
    model=settings.ollama_model,
)


curly = Curly(
    llm=llm,
    knowledge=knowledge,
)


tts = TTSService(
    output_dir="audio",
)


stt = STTService()


# ============================================================
# SERVICE STATUS
# ============================================================

print()

print("========== CURLY SERVICES CREATED ==========")


print(
    "Knowledge:",
    knowledge is not None,
)


print(
    "LLM:",
    llm is not None,
)


print(
    "Curly:",
    curly is not None,
)


print(
    "TTS:",
    tts is not None,
)


print(
    "STT:",
    stt is not None,
)


print("============================================")

print()


# ============================================================
# LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    # --------------------------------------------------------
    # STORE SERVICES IN APP STATE
    # --------------------------------------------------------

    app.state.knowledge = knowledge

    app.state.llm = llm

    app.state.curly = curly

    app.state.tts = tts

    app.state.stt = stt


    print("========== CURLY SERVICES READY ==========")


    print(
        "Knowledge:",
        app.state.knowledge is not None,
    )


    print(
        "LLM:",
        app.state.llm is not None,
    )


    print(
        "Curly:",
        app.state.curly is not None,
    )


    print(
        "TTS:",
        app.state.tts is not None,
    )


    print(
        "STT:",
        app.state.stt is not None,
    )


    print("==========================================")


    # --------------------------------------------------------
    # START LOCAL NETWORK DISCOVERY
    # --------------------------------------------------------

    discovery = CurlyServiceDiscovery()

    await discovery.start()


    # --------------------------------------------------------
    # APPLICATION RUNNING
    # --------------------------------------------------------

    yield


    # --------------------------------------------------------
    # STOP LOCAL NETWORK DISCOVERY
    # --------------------------------------------------------

    await discovery.stop()


    # --------------------------------------------------------
    # CLEANUP
    # --------------------------------------------------------

    app.state.knowledge = None

    app.state.llm = None

    app.state.curly = None

    app.state.tts = None

    app.state.stt = None


    await llm.close()


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Curly AI Backend",
    version="1.2.0",
    lifespan=lifespan,
)


# ============================================================
# MIDDLEWARE
# ============================================================

app.middleware("http")(
    request_id_middleware
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root():

    return {
        "service": "curly-ai",
        "status": "running",
        "version": "1.2.0",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
async def health():

    llm_service = getattr(
        app.state,
        "llm",
        None,
    )


    stt_available = (
        getattr(
            app.state,
            "stt",
            None,
        )
        is not None
    )


    tts_available = (
        getattr(
            app.state,
            "tts",
            None,
        )
        is not None
    )


    # --------------------------------------------------------
    # SERVICES STILL STARTING
    # --------------------------------------------------------

    if llm_service is None:

        return {
            "service": "curly-ai",
            "status": "starting",
            "ollama": {
                "server": False,
                "model": settings.ollama_model,
                "model_available": False,
                "models": [],
            },
            "model": settings.ollama_model,
            "stt": stt_available,
            "tts": tts_available,
        }


    # --------------------------------------------------------
    # OLLAMA HEALTH
    # --------------------------------------------------------

    try:

        ollama_status = await llm_service.health()


    except Exception:

        ollama_status = {
            "server": False,
            "model": settings.ollama_model,
            "model_available": False,
            "models": [],
        }


    # --------------------------------------------------------
    # HEALTH RESPONSE
    # --------------------------------------------------------

    return {
        "service": "curly-ai",
        "status": (
            "healthy"
            if (
                ollama_status.get("server")
                and ollama_status.get("model_available")
            )
            else "degraded"
        ),
        "ollama": ollama_status,
        "model": settings.ollama_model,
        "stt": stt_available,
        "tts": tts_available,
    }


# ============================================================
# CHAT ROUTER
# ============================================================

chat_router = create_chat_router(
    curly
)


print()

print("========== CHAT ROUTER ==========")


print(
    "Router type:",
    type(chat_router),
)


print(
    "Route count:",
    len(chat_router.routes),
)


for route in chat_router.routes:

    print(
        "CHAT ROUTE:",
        type(route),
        getattr(route, "methods", None),
        getattr(route, "path", None),
    )


print("=================================")


app.include_router(
    chat_router
)


# ============================================================
# TTS ROUTER
# ============================================================

tts_router = create_tts_router(
    tts=tts,
    curly=curly,
)


print()

print("========== TTS ROUTER ==========")


print(
    "Router type:",
    type(tts_router),
)


print(
    "Route count:",
    len(tts_router.routes),
)


for route in tts_router.routes:

    print(
        "TTS ROUTE:",
        type(route),
        getattr(route, "methods", None),
        getattr(route, "path", None),
    )


print("================================")


app.include_router(
    tts_router
)


# ============================================================
# STT ROUTER
# ============================================================

stt_router = create_stt_router(
    stt
)


print()

print("========== STT ROUTER ==========")


print(
    "Router type:",
    type(stt_router),
)


print(
    "Route count:",
    len(stt_router.routes),
)


for route in stt_router.routes:

    print(
        "STT ROUTE:",
        type(route),
        getattr(route, "methods", None),
        getattr(route, "path", None),
    )


print("================================")


app.include_router(
    stt_router
)


# ============================================================
# PROCESS ROUTER
# ============================================================

process_router = create_process_router(
    curly=curly,
    stt=stt,
)


print()

print("========== PROCESS ROUTER ==========")


print(
    "Router type:",
    type(process_router),
)


print(
    "Route count:",
    len(process_router.routes),
)


for route in process_router.routes:

    print(
        "PROCESS ROUTE:",
        type(route),
        getattr(route, "methods", None),
        getattr(route, "path", None),
    )


print("====================================")


app.include_router(
    process_router
)


# ============================================================
# VOICE ROUTER
# ============================================================

voice_router = create_voice_router(
    curly=curly,
    stt=stt,
    tts=tts,
)


print()

print("========== VOICE ROUTER DIAGNOSTIC ==========")


print(
    "Voice router object:",
    type(voice_router),
)


print(
    "Voice router routes:",
    len(voice_router.routes),
)


for route in voice_router.routes:

    print(
        "VOICE ROUTE:",
        type(route),
        getattr(route, "methods", None),
        getattr(route, "path", None),
    )


print("==============================================")


print()


app.include_router(
    voice_router
)


# ============================================================
# SESSION ROUTER
# ============================================================

session_router = create_session_router(
    curly
)


print()

print("========== SESSION ROUTER ==========")


print(
    "Router type:",
    type(session_router),
)


print(
    "Route count:",
    len(session_router.routes),
)


for route in session_router.routes:

    print(
        "SESSION ROUTE:",
        type(route),
        getattr(route, "methods", None),
        getattr(route, "path", None),
    )


print("====================================")


app.include_router(
    session_router
)


# ============================================================
# REGISTERED ROUTES
# ============================================================

print()

print("========== REGISTERED ROUTES ==========")


for route in app.routes:

    print(
        "ROUTE:",
        type(route),
        getattr(route, "methods", None),
        getattr(route, "path", None),
    )


print("=======================================")


# ============================================================
# OPENAPI ROUTE CHECK
# ============================================================

print()

print("========== OPENAPI ROUTE CHECK ==========")


try:

    openapi = app.openapi()


    paths = openapi.get(
        "paths",
        {}
    )


    print(
        "Total OpenAPI paths:",
        len(paths),
    )


    if "/v1/voice" in paths:

        print(
            "VOICE OPENAPI ROUTE FOUND:"
        )


        print(
            paths["/v1/voice"]
        )


    else:

        print(
            "VOICE OPENAPI ROUTE NOT FOUND"
        )


    print(
        "All API paths:"
    )


    for path in paths:

        print(
            "OPENAPI PATH:",
            path,
        )


except Exception as error:

    print(
        "OPENAPI CHECK FAILED:",
        error,
    )


print("==========================================")

print()