from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://changsu:changsu_pass@localhost:5432/changsu"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str = ""
    allowed_origins: list[str] = ["http://localhost:10086"]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
