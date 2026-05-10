import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")


@dataclass
class Settings:
    # Database
    db_host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    db_port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    db_name: str = field(default_factory=lambda: os.getenv("DB_NAME", "meshmind"))
    db_schema: str = field(default_factory=lambda: os.getenv("DB_SCHEMA", "meshmind"))
    db_user: str = field(default_factory=lambda: os.getenv("DB_USER", "postgres"))
    db_password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))

    # LLM
    deepseek_api_key: str = field(
        default_factory=lambda: os.getenv("ANTHROPIC_AUTH_TOKEN", "")
    )
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    llm_pro_model: str = field(default_factory=lambda: os.getenv("DEFAULT_MODEL", "deepseek-v4-pro"))
    llm_flash_model: str = field(default_factory=lambda: os.getenv("LLM_FLASH_MODEL", "deepseek-v4-flash"))

    # Embedding
    embedding_model: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
    )
    embedding_dim: int = field(
        default_factory=lambda: int(os.getenv("EMBEDDING_DIM", "1024"))
    )

    # Storage (MinIO/S3)
    s3_endpoint: str = field(default_factory=lambda: os.getenv("S3_ENDPOINT", "http://127.0.0.1:9000"))
    s3_access_key: str = field(default_factory=lambda: os.getenv("S3_ACCESS_KEY", ""))
    s3_secret_key: str = field(default_factory=lambda: os.getenv("S3_SECRET_KEY", ""))
    s3_bucket: str = field(default_factory=lambda: os.getenv("S3_BUCKET", "meshmind-documents"))
    s3_region: str = field(default_factory=lambda: os.getenv("S3_REGION", "us-east-1"))

    # JWT
    jwt_secret: str = field(
        default_factory=lambda: os.getenv("JWT_SECRET", "meshmind-dev-secret")
    )
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def db_sync_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
