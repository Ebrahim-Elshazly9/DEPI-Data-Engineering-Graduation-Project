from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    supabase_url: str = "https://jicivakvkucdufeuolvk.supabase.co"
    supabase_service_key: str = ""
    supabase_anon_key: str = ""

    ai_provider: str = "groq"
    ai_model: str = "llama-3.3-70b-versatile"
    openai_api_key: Optional[str] = None
    groq_api_key: Optional[str] = "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"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    openrouter_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"

    embedding_model: str = "text-embedding-3-small"

    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
