"""Global config to manage different codegen sessions, as well as user auth."""

# TODO: rename this file to global.py
import json
from pathlib import Path

from pydantic_settings import BaseSettings

from codegen.shared.configs.constants import SESSION_FILE


class GlobalSessionConfig(BaseSettings):
    active_session_path: str | None = None
    sessions: list[str]

    def get_active_session(self) -> Path | None:
        if not self.active_session_path:
            return None

        return Path(self.active_session_path)

    def set_active_session(self, session_root_path: Path) -> None:
        if not session_root_path.exists():
            msg = f"Session path does not exist: {session_root_path}"
            raise ValueError(msg)

        self.active_session_path = str(session_root_path)
        if session_root_path.name not in self.sessions:
            self.sessions.append(str(session_root_path))

    def save(self) -> None:
        if not SESSION_FILE.parent.exists():
            SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(SESSION_FILE, "w") as f:
            json.dump(self.model_dump(), f)


def _load_global_config() -> GlobalSessionConfig:
    """Load configuration from the JSON file."""
    if SESSION_FILE.exists():
        with open(SESSION_FILE) as f:
            json_config = json.load(f)
            return GlobalSessionConfig.model_validate(json_config, strict=False)

    new_config = GlobalSessionConfig(sessions=[])
    new_config.save()
    return new_config


config = _load_global_config()
