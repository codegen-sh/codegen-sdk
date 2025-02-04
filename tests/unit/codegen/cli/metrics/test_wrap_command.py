import pytest
from rich_click import argument, command, option

from codegen.cli.metrics.wrap_command import metrics_wrapper


def test_metrics_wrapper_success(mock_metrics_client):
    @command("test command")
    def test_command():
        return "success"

    wrapped_command = metrics_wrapper(test_command)
    result = wrapped_command([], standalone_mode=False)

    assert result == "success"
    mock_metrics_client.capture_event.assert_called_once_with(
        "command test command succeeded",
        {"duration": pytest.approx(0, abs=1e-2)},  # Allowing a small margin for time measurement
    )


def test_metrics_wrapper_with_args(mock_metrics_client):
    @command("test command")
    @argument("arg1")
    @option("--arg2", is_flag=True, default=False)
    def test_command(arg1, arg2=False):
        return f"success {arg1} {arg2}"

    wrapped_command = metrics_wrapper(test_command)
    result = wrapped_command(["arg1", "--arg2"], standalone_mode=False)

    assert result == "success arg1 True"
    mock_metrics_client.capture_event.assert_called_once_with(
        "command test command succeeded",
        {"duration": pytest.approx(0, abs=1e-2)},  # Allowing a small margin for time measurement
    )


def test_metrics_wrapper_failure(mock_metrics_client):
    @command("test command")
    def test_command():
        msg = "Test exception"
        raise Exception(msg)

    wrapped_command = metrics_wrapper(test_command)
    with pytest.raises(Exception, match="Test exception"):
        wrapped_command([], standalone_mode=False)

    mock_metrics_client.capture_event.assert_called_once_with(
        "command test command failed",
        {"duration": pytest.approx(0, abs=1e-2), "error": "Test exception"},
    )
