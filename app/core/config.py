from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Vehicle Check API"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000

    database_url: str = "postgresql+psycopg2://postgres:password@localhost:5432/vehicle_check_db"

    secret_key: str = "change_me_super_secret_key_2026_abcdef123456"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    supabase_url: str = ""
    supabase_key: str = ""
    supabase_storage_bucket: str = "vehicle-checks"

    agency_logo_path: str = "assets/logo.png"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()