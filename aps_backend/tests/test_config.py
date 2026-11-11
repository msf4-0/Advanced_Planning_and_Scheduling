"""Tests for the typed application settings and DatabaseConfig wiring."""

import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings
from repository import DatabaseConfig


def test_settings_read_the_existing_environment_names(monkeypatch):
    monkeypatch.setenv("POSTGRES_HOST", "db.internal")
    monkeypatch.setenv("POSTGRES_PORT", "6543")
    monkeypatch.setenv("POSTGRES_USER", "aps_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "aps_password")
    monkeypatch.setenv("POSTGRES_DB", "aps_test")
    monkeypatch.setenv("SOLVER_TIME_LIMIT_SECONDS", "90.5")
    monkeypatch.setenv("SOLVER_NUM_WORKERS", "2")
    monkeypatch.setenv("SOLVER_RANDOM_SEED", "7")
    monkeypatch.setenv("PLANNING_HORIZON_DAYS", "21")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("API_LEGACY_ENABLED", "false")
    monkeypatch.setenv("USE_ASYNC_RUNS", "true")

    settings = Settings()

    assert settings.postgres_host == "db.internal"
    assert settings.postgres_port == 6543
    assert settings.postgres_user == "aps_user"
    assert settings.postgres_password == "aps_password"
    assert settings.postgres_db == "aps_test"
    assert settings.solver_time_limit_seconds == 90.5
    assert settings.solver_num_workers == 2
    assert settings.solver_random_seed == 7
    assert settings.planning_horizon_days == 21
    assert settings.log_level == "DEBUG"
    assert settings.api_legacy_enabled is False
    assert settings.use_async_runs is True
    assert settings.database_kwargs() == {
        "host": "db.internal",
        "port": 6543,
        "user": "aps_user",
        "password": "aps_password",
        "dbname": "aps_test",
    }


def test_settings_validate_ranges_and_choices():
    with pytest.raises(ValidationError):
        Settings(postgres_port=70000)

    with pytest.raises(ValidationError):
        Settings(solver_num_workers=0)

    with pytest.raises(ValidationError):
        Settings(log_level="LOUD")


def test_get_settings_is_cached():
    get_settings.cache_clear()
    try:
        assert get_settings() is get_settings()
    finally:
        get_settings.cache_clear()


def test_database_config_accepts_explicit_settings_values():
    config = DatabaseConfig(
        host="db.internal",
        port=6543,
        user="aps_user",
        password="aps_password",
        dbname="aps_test",
    )

    assert config.to_dict() == {
        "host": "db.internal",
        "port": 6543,
        "user": "aps_user",
        "password": "aps_password",
        "dbname": "aps_test",
    }


def test_database_config_keeps_environment_fallback(monkeypatch):
    monkeypatch.setenv("POSTGRES_HOST", "legacy-host")

    assert DatabaseConfig().host == "legacy-host"
