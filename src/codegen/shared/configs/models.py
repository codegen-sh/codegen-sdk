from pathlib import Path

import toml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from codegen.shared.configs.constants import CONFIG_PATH, ENV_PATH


class TypescriptConfig(BaseModel):
    ts_dependency_manager: bool | None = None
    ts_language_engine: bool | None = None
    v8_ts_engine: bool | None = None


class CodebaseFeatureFlags(BaseModel):
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
        data = self.model_dump()
        keys = full_key.split(".")
        current = data
        for k in keys:
            if not isinstance(current, dict) or k not in current:
                return None
            current = current[k]
        return current

    def set(self, full_key: str, value: str) -> None:
        data = self.model_dump()
        keys = full_key.split(".")
        current = data
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        self.model_validate(data)
        self.save()

    def __str__(self) -> str:
        """Return a pretty-printed string representation of the config."""
        import json

        return json.dumps(self.model_dump(exclude_none=False), indent=2)
