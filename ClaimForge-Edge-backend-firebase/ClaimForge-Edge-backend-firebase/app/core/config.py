from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    hf_token: str = ""
    hf_vision_model: str = "moonshotai/Kimi-K3:baseten"
    hf_text_model: str = "openai/gpt-oss-120b:groq"
    firebase_service_account_path: str = "./firebase-service-account.json"
    firebase_service_account_json: str = ""
    firebase_storage_bucket: str = ""
    firebase_claims_collection: str = "claims"
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "*"
    max_upload_mb: int = 50
    analysis_timeout_seconds: int = 15
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

settings = Settings()
