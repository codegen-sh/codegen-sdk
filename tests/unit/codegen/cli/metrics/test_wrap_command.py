from unittest.mock import MagicMock

import pytest
from rich_click import RichCommand

from src.codegen.cli.metrics.wrap_command import metrics_wrapper


def test_metrics_wrapper_success(mock_metrics_client):
    def test_command():
        return "success"

    mock_command = MagicMock(spec=RichCommand)
    mock_command.name = "test_command"
    mock_command.callback = test_command
    mock_command.side_effect = test_command

    wrapped_command = metrics_wrapper(mock_command)
    result = wrapped_command()

    assert result == "success"
    mock_metrics_client.capture_event.assert_called_once_with(
        "command test_command succeeded",
        {"duration": pytest.approx(0, abs=1e-2)},  # Allowing a small margin for time measurement
    )


def test_metrics_wrapper_failure(mock_metrics_client):
    def test_command():
        msg = "Test exception"
        raise Exception(msg)

    mock_command = MagicMock(spec=RichCommand)
    mock_command.name = "test_command"
    mock_command.callback = test_command
    mock_command.side_effect = test_command

    wrapped_command = metrics_wrapper(mock_command)
    with pytest.raises(Exception, match="Test exception"):
        wrapped_command()

    mock_metrics_client.capture_event.assert_called_once_with(
        "command test_command failed",
        {"duration": pytest.approx(0, abs=1e-2), "error": "Test exception"},
    )
