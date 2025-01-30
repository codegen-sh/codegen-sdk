import uuid
from functools import lru_cache
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir
from pydantic import BaseModel, Field, field_validator

CONFIG_PATH = Path(user_config_dir("codegen")) / "config.json"
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists


class CLIUserConfigs(BaseModel, validate_assignment=True):
    anon_session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    is_metrics_enabled: bool | None = None

    @field_validator("is_metrics_enabled", mode="before")
    def prompt(cls, v: bool | None) -> Any:
        if v is None:
            response = input("To help us improve Codegen, would you like to opt in to anonymous usage metrics? (y/n) ")
            if response.strip().lower() == "y":
                return True
            else:
                return False
        return v

    def save(self):
        with open(CONFIG_PATH, "w") as f:
            f.write(self.model_dump_json(indent=2))

    @classmethod
    @lru_cache(maxsize=1)
    def load(cls) -> "CLIUserConfigs":
        if not CONFIG_PATH.exists():
            configs = cls()
            configs.save()
            return configs
        else:
            with open(CONFIG_PATH) as f:
                return cls.model_validate_json(f.read())
