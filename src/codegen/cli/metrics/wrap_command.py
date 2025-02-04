import functools
import time
from collections.abc import Callable

from rich_click import RichCommand

from codegen.cli.metrics.client import get_metrics_client


def metrics_wrapper(f: RichCommand) -> Callable:
    metrics_client = get_metrics_client()

    @functools.wraps(f.callback)
    def wrapper(*args, **kwargs):
        try:
            start_time = time.time()
            result = f(*args, **kwargs)
        except Exception as e:
            metrics_client.capture_event(f"command {f.name} failed", {"duration": time.time() - start_time, "error": str(e)})
            raise
        else:
            metrics_client.capture_event(f"command {f.name} succeeded", {"duration": time.time() - start_time})
            return result

    return wrapper
