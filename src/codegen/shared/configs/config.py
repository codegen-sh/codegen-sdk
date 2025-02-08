from pathlib import Path

import tomllib

from codegen.shared.configs.constants import CONFIG_PATH
from codegen.shared.configs.models import Config


def load(config_path: Path | None = None) -> Config:
    """Load configuration from the config file."""
    # Load from .env file
    env_config = _load_from_env()

    # Load from .codegen/config.toml file
    toml_config = _load_from_toml(config_path or CONFIG_PATH)

    # Merge configurations recursively
    config_dict = _merge_configs(env_config.model_dump(), toml_config.model_dump())

    return Config(**config_dict)


def _load_from_env() -> Config:
    """Load configuration from the environment variables."""
    return Config()


def _load_from_toml(config_path: Path) -> Config:
    """Load configuration from the TOML file."""
    if config_path.exists():
        with open(config_path, "rb") as f:
            toml_config = tomllib.load(f)
            return Config.model_validate(toml_config)
    return Config()


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


config = load()

if __name__ == "__main__":
    print(config)
