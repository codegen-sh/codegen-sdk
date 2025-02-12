# TODO: rename this file to local.py
import json
from pathlib import Path

import tomllib

from codegen.shared.configs.constants import CONFIG_PATH, SESSION_FILE
from codegen.shared.configs.models.global_session import GlobalSessionConfig
from codegen.shared.configs.models.session import SessionConfig


def load_session_config(config_path: Path) -> SessionConfig:
    """Loads configuration from various sources."""
    # Load from .env file
    env_config = _load_from_env(config_path)

    # Load from .codegen/config.toml file
    toml_config = _load_from_toml(config_path)

    # Merge configurations recursively
    config_dict = _merge_configs(env_config.model_dump(), toml_config.model_dump())
    loaded_config = SessionConfig(**config_dict)

    # Save the configuration to file if it doesn't exist
    if not config_path.exists():
        loaded_config.save()
    return loaded_config


def _load_from_env(config_path: Path) -> SessionConfig:
    """Load configuration from the environment variables."""
    return SessionConfig(file_path=str(config_path))


def _load_from_toml(config_path: Path) -> SessionConfig:
    """Load configuration from the TOML file."""
    if config_path.exists():
        with open(config_path, "rb") as f:
            toml_config = tomllib.load(f)
            toml_config["file_path"] = str(config_path)
            return SessionConfig.model_validate(toml_config, strict=False)

    return SessionConfig(file_path=str(config_path))


def _merge_configs(base: dict, override: dict) -> dict:
    """Recursively merge two dictionaries, with override taking precedence for non-null values."""
    merged = base.copy()
    for key, override_value in override.items():
        if isinstance(override_value, dict) and key in base and isinstance(base[key], dict):
            # Recursively merge nested dictionaries
            merged[key] = _merge_configs(base[key], override_value)
        elif override_value is not None and override_value != "":
            # Override only if value is non-null and non-empty
            merged[key] = override_value
    return merged


def _load_global_config() -> GlobalSessionConfig:
    """Load configuration from the JSON file."""
    if SESSION_FILE.exists():
        with open(SESSION_FILE) as f:
            json_config = json.load(f)
            return GlobalSessionConfig.model_validate(json_config, strict=False)

    new_config = GlobalSessionConfig(sessions=[])
    new_config.save()
    return new_config


config = load_session_config(CONFIG_PATH)
global_config = _load_global_config()


if __name__ == "__main__":
    print(config)
    print(global_config)
