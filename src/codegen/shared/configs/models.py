import json
from pathlib import Path

import toml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from codegen.shared.configs.constants import CONFIG_PATH, ENV_PATH


def _get_setting_config(group_name: str) -> SettingsConfigDict:
    return SettingsConfigDict(
        env_prefix=f"CODEGEN_{group_name}__",
        env_file=ENV_PATH,
        case_sensitive=False,
        extra="ignore",
        exclude_defaults=False,
    )


class TypescriptConfig(BaseSettings):
    model_config = _get_setting_config("FEATURE_FLAGS_TYPESCRIPT")
    ts_dependency_manager: bool | None = None
    ts_language_engine: bool | None = None
    v8_ts_engine: bool | None = None


class CodebaseFeatureFlags(BaseSettings):
    model_config = _get_setting_config("FEATURE_FLAGS")
    debug: bool | None = None
    verify_graph: bool | None = None
    track_graph: bool | None = None
    method_usages: bool | None = None
    sync_enabled: bool | None = None
    full_range_index: bool | None = None
    ignore_process_errors: bool | None = None
    disable_graph: bool | None = None
    generics: bool | None = None
    import_resolution_overrides: dict[str, str] = Field(default_factory=lambda: {})
    typescript: TypescriptConfig = Field(default_factory=TypescriptConfig)


class RepositoryConfig(BaseSettings):
    """Configuration for the repository context to run codegen.
    To populate this config, call `codegen init` from within a git repository.
    """

    model_config = _get_setting_config("REPOSITORY")

    repo_path: str | None = None
    repo_name: str | None = None
    full_name: str | None = None
    language: str | None = None
    user_name: str | None = None
    user_email: str | None = None


class SecretsConfig(BaseSettings):
    model_config = _get_setting_config("SECRETS")
    github_token: str | None = None
    openai_api_key: str | None = None


class FeatureFlagsConfig(BaseModel):
    codebase: CodebaseFeatureFlags = Field(default_factory=CodebaseFeatureFlags)


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        exclude_defaults=False,
    )
    secrets: SecretsConfig = Field(default_factory=SecretsConfig)
    repository: RepositoryConfig = Field(default_factory=RepositoryConfig)
    feature_flags: FeatureFlagsConfig = Field(default_factory=FeatureFlagsConfig)

    def save(self, config_path: Path | None = None) -> None:
        """Save configuration to the config file."""
        path = config_path or CONFIG_PATH

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            toml.dump(self.model_dump(exclude_none=True), f)

    def get(self, full_key: str) -> str | None:
        """Get a configuration value as a JSON string."""
        data = self.model_dump()
        keys = full_key.split(".")
        current = data
        for k in keys:
            if not isinstance(current, dict) or k not in current:
                return None
            current = current[k]
        return json.dumps(current)

    def set(self, full_key: str, value: str) -> None:
        """Update a configuration value and save it to the config file.

        Args:
            full_key: Dot-separated path to the config value (e.g. "feature_flags.codebase.debug")
            value: string representing the new value
        """
        data = self.model_dump()
        keys = full_key.split(".")
        current = data
        current_attr = self

        # Traverse through the key path and validate
        for k in keys[:-1]:
            if not isinstance(current, dict) or k not in current:
                msg = f"Invalid configuration path: {full_key}"
                raise KeyError(msg)
            current = current[k]
            current_attr = current_attr.__getattribute__(k)

        if not isinstance(current, dict) or keys[-1] not in current:
            msg = f"Invalid configuration path: {full_key}"
            raise KeyError(msg)

        # Validate the value type at key
        field_info = current_attr.model_fields[keys[-1]].annotation
        if isinstance(field_info, BaseModel):
            try:
                Config.model_validate(value, strict=False)
            except Exception as e:
                msg = f"Value does not match the expected type for key: {full_key}\n\nError:{e}"
                raise ValueError(msg)

        # Set the key value
        if isinstance(current[keys[-1]], dict):
            try:
                current[keys[-1]] = json.loads(value)
            except json.JSONDecodeError as e:
                msg = f"Value must be a valid JSON object for key: {full_key}\n\nError:{e}"
                raise ValueError(msg)
        else:
            current[keys[-1]] = value

        # Update the Config object with the new data
        self.__dict__.update(self.__class__.model_validate(data).__dict__)

        # Save to config file
        self.save()

    def __str__(self) -> str:
        """Return a pretty-printed string representation of the config."""
        return json.dumps(self.model_dump(exclude_none=False), indent=2)
