# Curly AI Production / Handoff Checklist

## Backend

- [x] FastAPI application starts
- [x] Health endpoint returns a structured dependency status
- [x] Session management implemented
- [x] Deterministic intent routing implemented
- [x] Deterministic person resolution implemented
- [x] Institutional knowledge separated from LLM generation
- [x] Whisper STT integrated
- [x] Ollama + Llama 3.1 8B integrated
- [x] Edge TTS integrated
- [x] Cross-platform desktop audio path tested
- [x] Automated test suite green

## Configuration

- [x] Real `.env` excluded from version control
- [x] `.env.example` provided
- [x] Ollama model name is explicit
- [x] STT model/device/compute settings are explicit
- [x] History and session limits are explicit

## Security hardening before public deployment

- [ ] Put the API behind HTTPS or an authenticated reverse proxy.
- [ ] Do not expose unauthenticated `/v1/events` to an untrusted network.
- [ ] Treat client-supplied authentication results as untrusted until the Android/auth channel is secured.
- [ ] Keep request/upload size limits on every audio endpoint.
- [ ] Never return raw internal exception strings to clients.
- [ ] Add rate limiting at the deployment edge.
- [ ] Restrict CORS only if a browser client is added; native Android does not require browser CORS.
- [ ] Add structured access logging and rotate logs.
- [ ] Run the service under a dedicated OS account in production.

## Android handoff

- [ ] Share `docs/API.md`
- [ ] Share backend LAN-IP configuration instructions
- [ ] Share session lifecycle expectations
- [ ] Share `/v1/voice` multipart format
- [ ] Share event types and authentication flow
- [ ] Confirm Android uses `session_id` consistently

## Release

- [ ] Run `pytest -q`
- [ ] Run `scripts/check_curly.ps1`
- [ ] Verify `git status` contains no `.env`, model files, audio artifacts, or caches
- [ ] Verify the backend starts from a clean environment
- [ ] Tag the backend release
