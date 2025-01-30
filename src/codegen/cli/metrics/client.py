import atexit
import platform
from concurrent.futures import ThreadPoolExecutor
from functools import cached_property
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

    @cached_property
    def platform_info(self) -> dict[str, str]:
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "python_version": platform.python_version(),
            "codegen_version": global_env.VERSION,
        }

    def capture_event(self, event_name: str, properties: dict[str, Any] | None = None) -> None:
        """Capture an event if user has opted in."""
        if not self.configs.is_metrics_enabled:
            return
        properties = properties or {}
        try:
            self.pool.submit(
                self.posthog.capture,
                distinct_id=self.session_id,
                event=event_name,
                properties={**self.platform_info, **properties},
                groups={"codegen_app": "cli"},
            )
        except Exception as e:
            pass


if __name__ == "__main__":
    posthog = MetricsClient()
    posthog.capture_event("test")
