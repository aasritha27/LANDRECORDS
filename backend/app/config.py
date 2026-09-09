import os
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    from pydantic import BaseSettings
    SettingsConfigDict = None

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Land Record Digitization & Validation System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgrespassword@localhost:5432/land_records"
    )
    SYNC_DATABASE_URL: str = os.getenv(
        "SYNC_DATABASE_URL",
        "postgresql://postgres:postgrespassword@localhost:5432/land_records"
    )

    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    PREPROCESSED_DIR: str = os.path.join(UPLOAD_DIR, "preprocessed")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production-123456789")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Confidence Thresholds
    # Calibrated for real OCR confidence (not hardcoded values).
    # A document needs ≥70% real confidence across all fields to be auto-validated.
    # Anything below routes to human review queue.
    CONFIDENCE_THRESHOLD_AUTO_VALIDATE: float = 0.70

    if SettingsConfigDict:
        model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")
    else:
        class Config:
            case_sensitive = True

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PREPROCESSED_DIR, exist_ok=True)
