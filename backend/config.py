from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    model: str = "anthropic/claude-haiku-4-5"

    mcp_server_url: str = "https://order-mcp-74afyau24q-uc.a.run.app/mcp"

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


settings = Settings()  # type: ignore[call-arg]
