import base64
import os

from pydantic import BaseModel
from pydantic.config import ConfigDict

from codegen.git.schemas.repo_config import RepoConfig
from codegen.runner.constants.envvars import FEATURE_FLAGS_BASE64, REPO_CONFIG_BASE64
from codegen.sdk.codebase.config import CodebaseConfig, GSFeatureFlags
from codegen.sdk.secrets import Secrets


class RunnerFeatureFlags(BaseModel):
    """Feature flags for a runner"""

    model_config = ConfigDict(frozen=True)

    sync_enabled: bool = True
    track_graph: bool = False
    verify_graph: bool = False

    ts_language_engine: bool = False
    v8_ts_engine: bool = False
    ts_dependency_manager: bool = False

    import_resolution_overrides: dict[str, str] = {}

    def encoded_json(self):
        return base64.b64encode(self.model_dump_json().encode("utf-8")).decode("utf-8")

    @staticmethod
    def from_encoded_json(encoded_json: str) -> "RunnerFeatureFlags":
        decoded = base64.b64decode(encoded_json).decode("utf-8")
        return RunnerFeatureFlags.model_validate_json(decoded)


def get_codebase_config() -> CodebaseConfig:
    gs_ffs = GSFeatureFlags(**get_runner_feature_flags().model_dump())
    secrets = Secrets(openai_key=os.environ["OPENAI_PASS"])
    return CodebaseConfig(secrets=secrets, feature_flags=gs_ffs)


def get_runner_feature_flags() -> RunnerFeatureFlags:
    encoded_ffs = os.environ.get(FEATURE_FLAGS_BASE64)
    if not encoded_ffs:
        msg = "FEATURE_FLAGS_BASE64 environment variable not found"
        raise ValueError(msg)
    return RunnerFeatureFlags.from_encoded_json(encoded_ffs)


def get_repo_config() -> RepoConfig:
    encoded_repo_config = os.environ.get(REPO_CONFIG_BASE64)
    if not encoded_repo_config:
        msg = "REPO_CONFIG_BASE64 environment variable not found"
        raise ValueError(msg)
    return RepoConfig.from_encoded_json(encoded_repo_config)
