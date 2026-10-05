# Curly AI Backend API

Base URL:

http://<SERVER-IP>:8000

For local testing:

http://127.0.0.1:8000


## Health

### GET /health

Returns backend and dependency status.

Example:

{
  "service": "curly-ai",
  "status": "healthy",
  "ollama": {
    "server": true,
    "model": "llama3.1:8b",
    "model_available": true,
    "models": [...]
  },
  "model": "llama3.1:8b",
  "stt": true,
  "tts": true
}


## Sessions

### POST /v1/session

Creates a new Curly session.

Response:

{
  "session_id": "..."
}


### GET /v1/session/{session_id}/state

Returns the current Curly state.

### DELETE /v1/session/{session_id}

Deletes the session.


## Chat

### POST /v1/chat

Text-based conversation.

Input:

{
  "session_id": "...",
  "text": "Who is Dr. Mihir Sarkar?"
}

Flow:

text
→ Curly deterministic routing
→ knowledge/person/command resolver
→ Llama 3.1 8B when required


## Voice

### POST /v1/voice

Multipart form:

session_id=<session>
file=<audio file>
context=<optional JSON object>

Flow:

audio
→ Whisper Base
→ Curly
→ deterministic routing / Llama
→ Edge TTS
→ audio/mpeg response


## Process

### POST /v1/process

Multipart form:

session_id=<session>
file=<audio file>
context=<optional JSON object>

Returns:

transcription
Curly response
STT latency
Curly latency
total latency


## STT

### POST /v1/stt

Accepts an audio file and returns the Whisper transcription.


## TTS

### POST /v1/tts

Accepts text and returns generated speech audio.


## Events

### POST /v1/events

Used for Android/backend events such as:

AUTH_RESULT
TIME_RESULT
WEATHER_RESULT