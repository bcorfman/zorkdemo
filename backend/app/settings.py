"""Backend runtime settings."""

from environs import Env


env = Env()
env.read_env()


class Settings:
    def __init__(self) -> None:
        self.database_url = env.str("DATABASE_URL", default="sqlite:///sessions.db")
        self.cors_allow_origins = self._parse_origins(
            env.str(
                "CORS_ALLOW_ORIGINS",
                default="http://localhost:5173,http://localhost:8000",
            )
        )

    @staticmethod
    def _parse_origins(raw_origins: str) -> list[str]:
        origins: list[str] = []
        for origin in raw_origins.split(","):
            value = origin.strip()
            if value:
                origins.append(value)
        return origins


settings = Settings()
