import uuid
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

from platformdirs import user_config_dir
from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator

from codegen.cli.env.global_env import global_env

CONFIG_PATH: Path = Path(global_env.CONFIG_PATH) if global_env.CONFIG_PATH else Path(user_config_dir("codegen")) / "config.json"
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists


PROMPT_TO_ENV_MAPPING: dict[str, str] = {
    "is_metrics_enabled": global_env.METRICS_ENABLED,
}


class CLIUserConfigs(BaseModel, validate_assignment=True):
    anon_session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    is_metrics_enabled: bool = Field(
        validate_default=True,
        description="To help us improve Codegen, would you like to opt in to anonymous usage metrics? [y/n] ",
    )

    def __init__(self, /, **kwargs):
        self.__pydantic_validator__.validate_python(kwargs, self_instance=self, context={"no-save": False})

    @classmethod
    def prompt(cls, v: Any, info: ValidationInfo) -> Any:
        if not info.field_name:
            # Not a field with prompting enabled.
            return v

        field_info = cls.model_fields[info.field_name]
        if v is None:
            # Global env uses "" to indicate that the env var is not set, so we need to handle that case
            env_value: str = PROMPT_TO_ENV_MAPPING[info.field_name]
            if env_value != "":
                return env_value

            cast(dict, info.context)["no-save"] = False
            response = input(field_info.description)
            v = response.strip()
        return v

    @field_validator("is_metrics_enabled", mode="before")
    @classmethod
    def validate_boolean_input(cls, v: Any, info: ValidationInfo) -> bool:
        v = cls.prompt(v, info)
        if isinstance(v, str):
            v = v.strip().lower()
            return v == "y"
        return v

    @model_validator(mode="after")
    def save_changes(self, info: ValidationInfo) -> "CLIUserConfigs":
        if info.context and not cast(dict, info.context).get("no-save"):
            self.save()
        return self

    def save(self):
        with CONFIG_PATH.open("w") as f:
            f.write(self.model_dump_json(indent=2))

    @classmethod
    @lru_cache(maxsize=1)
    def load(cls) -> "CLIUserConfigs":
        if not CONFIG_PATH.exists():
            return CLIUserConfigs()
        else:
            with CONFIG_PATH.open("r") as f:
                return cls.model_validate_json(f.read(), context={"no-save": True})
