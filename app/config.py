from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # --------------------------------
    # Ollama
    # --------------------------------

    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    # --------------------------------
    # LLM / Ollama
    # --------------------------------

    llm_temperature: float = 0.2
    llm_max_tokens: int = 96
    ollama_num_ctx: int = 2048
    ollama_keep_alive: str = "5m"
    
    # --------------------------------
    # Conversation
    # --------------------------------

    max_history: int = 7

    # --------------------------------
    # Session Timeout
    # --------------------------------

    session_timeout_seconds: int = 300

    # --------------------------------
    # Server
    # --------------------------------

    host: str = "0.0.0.0"
    port: int = 8000

    # --------------------------------
    # TTS
    # --------------------------------

    tts_voice: str = "en-US-JennyNeural"
    tts_rate: str = "+0%"
    tts_volume: str = "+0%"

    # --------------------------------
    # STT
    # --------------------------------

    stt_model: str = "small"
    stt_device: str = "cpu"
    stt_compute_type: str = "int8"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()