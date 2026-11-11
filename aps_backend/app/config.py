"""Typed application settings.

Environment variable names are preserved for deployment compatibility:

- ``POSTGRES_HOST``, ``POSTGRES_PORT``, ``POSTGRES_USER``,
  ``POSTGRES_PASSWORD``, ``POSTGRES_DB``
- ``SOLVER_TIME_LIMIT_SECONDS``, ``SOLVER_NUM_WORKERS``,
  ``SOLVER_RANDOM_SEED``, ``PLANNING_HORIZON_DAYS``
- ``LOG_LEVEL``
- ``API_LEGACY_ENABLED``, ``USE_ASYNC_RUNS`` (reserved migration flags)

Values are read from the process environment. Docker Compose supplies them via
``docker-compose.yaml``; no implicit ``.env`` loading is performed here.
"""

from functools import lru_cache
from typing import Literal, TypedDict

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseKwargs(TypedDict):
    host: str
    port: int
    user: str
    password: str
    dbname: str


class Settings(BaseSettings):
    """Single typed source of runtime configuration."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    postgres_host: str = "postgres"
    postgres_port: int = Field(default=5432, ge=1, le=65535)
    postgres_user: str = "postgresUser"
    postgres_password: str = "postgresPass"
    postgres_db: str = "postgresDB"

    # Scheduling policy. These are consumed by the Phase 3 solver extraction;
    # keeping them typed here avoids scattering magic numbers in the pipeline.
    solver_time_limit_seconds: float = Field(default=60.0, gt=0)
    solver_num_workers: int = Field(default=4, ge=1)
    solver_random_seed: int = 0
    planning_horizon_days: int = Field(default=14, ge=1)

    # Operations
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # Migration flags reserved for the API/worker cut-over.
    api_legacy_enabled: bool = True
    use_async_runs: bool = False

    def database_kwargs(self) -> DatabaseKwargs:
        """Connection parameters for the repository's DatabaseConfig."""
        return {
            "host": self.postgres_host,
            "port": self.postgres_port,
            "user": self.postgres_user,
            "password": self.postgres_password,
            "dbname": self.postgres_db,
        }


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings instance (FastAPI dependency-safe)."""
    return Settings()
