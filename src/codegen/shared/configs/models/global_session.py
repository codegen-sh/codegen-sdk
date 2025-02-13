"""Global config to manage different codegen sessions, as well as user auth."""

import json
from pathlib import Path

from pydantic_settings import BaseSettings

from codegen.shared.configs.constants import SESSION_FILE


class GlobalSessionConfig(BaseSettings):
    active_session_path: str | None = None
    sessions: list[str]

    def get_session(self, session_root_path: Path) -> str | None:
        return next((s for s in self.sessions if s == str(session_root_path)), None)

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

        self.save()

    def save(self) -> None:
        if not SESSION_FILE.parent.exists():
            SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(SESSION_FILE, "w") as f:
            json.dump(self.model_dump(), f)
