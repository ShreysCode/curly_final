# Curly AI Backend

Curly AI is a Python/FastAPI voice-assistant backend for an Android client. The backend handles speech-to-text, deterministic institutional routing, LLM conversation, text-to-speech, sessions, and Android events.

## Architecture

```text
Android / Desktop client
          |
          v
      FastAPI
          |
        Curly
     /     |      \
    /      |       \
  STT   Deterministic  LLM
        routing/KB    Ollama
                         |
                    Llama 3.1 8B
          |
          v
       Edge TTS
          |
          v
       audio/mpeg
```

The Android client owns production microphone, speaker, camera, wake-word, and UI behavior. The backend owns Curly logic and AI services.

## Stack

- Python
- FastAPI / Uvicorn
- faster-whisper (Whisper Base, CPU/int8)
- Ollama + `llama3.1:8b`
- Edge TTS
- PyAV
- sounddevice
- Pydantic / pydantic-settings
- pytest / pytest-asyncio

## Requirements

- Python 3.14 environment used by the current development setup
- Ollama installed and serving `llama3.1:8b`
- Working microphone/audio device for `run_voice.py`
- Network access for Edge TTS

## Windows Ollama

The model store is intended to live on D:.

```powershell
$env:OLLAMA_MODELS="D:\Ollama\Models"
ollama serve
```

Keep exactly one Ollama server bound to port `11434`.

Verify:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

The response should contain `llama3.1:8b`.

## Python setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and adjust values for the machine.

## Start backend

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or use:

```powershell
.\scripts\start_curly.ps1
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## Desktop voice harness

```powershell
python .\run_voice.py
```

The desktop harness is for development/testing. It is not the final Android audio implementation.

## Tests

Run the complete suite from the repository root:

```powershell
pytest -q
```

The release baseline is the locally verified green test suite.

## API

Full API details are in [`docs/API.md`](docs/API.md).

Main endpoints:

- `GET /health`
- `POST /v1/session`
- `GET /v1/session/{session_id}/state`
- `DELETE /v1/session/{session_id}`
- `POST /v1/chat`
- `POST /v1/voice`
- `POST /v1/process`
- `POST /v1/stt`
- `POST /v1/tts`
- `POST /v1/events`

## Core voice flow

```text
Microphone
  -> Whisper Base
  -> speech normalization
  -> deterministic Curly routing
  -> knowledge/person/command resolution
  -> Llama 3.1 8B when required
  -> Edge TTS
  -> audio/mpeg
  -> client playback
```

Known institutional people and structured facts should be answered deterministically whenever possible. The LLM is the fallback for general conversation and questions that require generation.

## Configuration

Important settings:

```text
OLLAMA_URL
OLLAMA_MODEL
LLM_TEMPERATURE
LLM_MAX_TOKENS
OLLAMA_NUM_CTX
OLLAMA_KEEP_ALIVE
MAX_HISTORY
SESSION_TIMEOUT_SECONDS
TTS_VOICE
TTS_RATE
TTS_VOLUME
STT_MODEL
STT_DEVICE
STT_COMPUTE_TYPE
HOST
PORT
```

Never commit the real `.env` file.

## Project data

Institutional information is stored in:

```text
app/knowledge/data.json
app/knowledge/info_repo.json
```

Do not silently invent or alter institutional facts during refactoring.

## Android integration

For a physical Android device, do not use `localhost` for the backend. Use the Windows/macOS host's LAN IP:

```text
http://<HOST-LAN-IP>:8000
```

The Android client should create a session first, then use the returned `session_id` for chat/voice/event requests.

## Project status

Backend/AI runtime:

- FastAPI backend: working
- Llama/Ollama: working
- Whisper STT: working
- Edge TTS: working
- Desktop voice loop: working
- Automated tests: green

Android client development is a separate workstream.
