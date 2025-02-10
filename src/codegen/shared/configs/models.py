import json
from pathlib import Path

import toml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from codegen.shared.configs.constants import CONFIG_PATH, ENV_PATH


class TypescriptConfig(BaseModel):
    ts_dependency_manager: bool = False
    ts_language_engine: bool = False
    v8_ts_engine: bool = False


class CodebaseFeatureFlags(BaseModel):
    debug: bool = False
    verify_graph: bool = False
    track_graph: bool = False
    method_usages: bool = True
    sync_enabled: bool = True
    full_range_index: bool = False
    ignore_process_errors: bool = True
    disable_graph: bool = False
    generics: bool = True
    import_resolution_overrides: dict[str, str] = Field(default_factory=lambda: {})
    typescript: TypescriptConfig = Field(default_factory=TypescriptConfig)


class RepositoryConfig(BaseModel):
    organization_name: str | None = None
    repo_name: str | None = None


class SecretsConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CODEGEN_SECRETS__",
        env_file=ENV_PATH,
        case_sensitive=False,
    )
    github_token: str | None = None
    openai_api_key: str | None = None


class FeatureFlagsConfig(BaseModel):
    syntax_highlight_enabled: bool | None = None
    codebase: CodebaseFeatureFlags = Field(default_factory=CodebaseFeatureFlags)


class Config(BaseSettings):
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
        # Navigate to the correct nested dictionary
        data = self.model_dump()
        keys = full_key.split(".")
        current = data

        # Traverse until the second-to-last key
        for k in keys[:-1]:
            if not isinstance(current, dict) or k not in current:
                msg = f"Invalid configuration path: {full_key}"
                raise KeyError(msg)
            current = current[k]

        # Set the value at the final key
        if not isinstance(current, dict) or keys[-1] not in current:
            msg = f"Invalid configuration path: {full_key}"
            raise KeyError(msg)

        if isinstance(current[keys[-1]], dict):
            current[keys[-1]] = json.loads(value)
        else:
            current[keys[-1]] = value

        # Update the Config object with the new data
        self.__dict__.update(self.__class__.model_validate(data).__dict__)

        # Save to config file
        self.save()

    def __str__(self) -> str:
        """Return a pretty-printed string representation of the config."""
        return json.dumps(self.model_dump(exclude_none=False), indent=2)
