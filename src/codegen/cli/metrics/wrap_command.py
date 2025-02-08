import functools
import time

from click import Command

from codegen.cli.metrics.client import get_metrics_client


def metrics_wrapper(f: Command) -> Command:
    metrics_client = get_metrics_client()

    if f.callback is None:
        msg = "Command callback is not set. Wrapper must be used with a command that has a function"
        raise ValueError(msg)

    command_fn = f.callback

    @functools.wraps(command_fn)
    def wrapper(*args, **kwargs):
        try:
            start_time = time.time()
            result = command_fn(*args, **kwargs)
        except Exception as e:
            metrics_client.capture_event(f"command {f.name} failed", {"duration": time.time() - start_time, "error": str(e)})
            raise
        else:
            metrics_client.capture_event(f"command {f.name} succeeded", {"duration": time.time() - start_time})
            return result

    f.callback = wrapper
    return f
