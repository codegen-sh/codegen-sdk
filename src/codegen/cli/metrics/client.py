import atexit
import platform
import traceback
from concurrent.futures import ThreadPoolExecutor
from functools import cached_property
from importlib.metadata import PackageNotFoundError, distribution, version
from typing import Any

from posthog import Posthog

from codegen.cli.config import CLIUserConfigs
from codegen.cli.env.global_env import global_env


class MetricsClient:
    posthog: Posthog

    def __init__(self):
        self.configs = CLIUserConfigs.load()
        self.session_id = self.configs.anon_session_id
        self.posthog = Posthog(global_env.POSTHOG_PROJECT_API_KEY, host="https://us.i.posthog.com")
        self.pool = ThreadPoolExecutor()
        atexit.register(self.pool.shutdown)
        self.posthog.disabled = not self.configs.is_metrics_enabled

    @cached_property
    def platform_info(self) -> dict[str, str]:
        try:
            version_str: str = version(distribution(__package__).metadata["Name"])
        except PackageNotFoundError:
            version_str = "dev"

        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "python_version": platform.python_version(),
            "codegen_version": version_str,
        }

    def capture_event(self, event_name: str, properties: dict[str, Any] | None = None) -> None:
        """Capture an event if user has opted in."""
        properties = properties or {}
        try:
            self.pool.submit(
                self.posthog.capture,
                distinct_id=self.session_id,
                event=event_name,
                properties={**self.platform_info, **properties},
                groups={"platform": "cli"},
            )
        except Exception:
            if global_env.DEBUG:
                traceback.print_exc()


if __name__ == "__main__":
    posthog = MetricsClient()
    posthog.capture_event("test")
