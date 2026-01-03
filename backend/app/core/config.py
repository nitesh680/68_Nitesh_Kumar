from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URI: str
    MONGODB_DB: str = "expense_ai"

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30

    GEMINI_API_KEY: str | None = None

    CORS_ORIGINS: str = "http://localhost:5173"

    MODEL_DIR: str = "./artifacts"
    CONFIDENCE_THRESHOLD: float = 0.65

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
