from unittest.mock import MagicMock, patch

import pytest

from codegen.cli.metrics.client import MetricsClient, get_metrics_client


@pytest.fixture
def atexit_mock():
    with patch("src.codegen.cli.metrics.client.atexit.register") as mock:
        yield mock


@pytest.fixture
def mock_posthog():
    mock_posthog = MagicMock()
    with patch("src.codegen.cli.metrics.client.Posthog", return_value=mock_posthog):
        yield mock_posthog


@pytest.fixture(autouse=True)
def mock_metrics_client(mock_cli_user_configs, atexit_mock, mock_posthog):
    # Disables conftest metrics client mock by replacing it
    mock_cli_user_configs.is_metrics_enabled = False
    with patch("src.codegen.cli.metrics.client.ThreadPoolExecutor"):
        yield MetricsClient()


def test_get_metrics_client():
    client1 = get_metrics_client()
    client2 = get_metrics_client()
    assert client1 is client2  # lru_cache should return the same instance


def test_client_init(mock_metrics_client, mock_cli_user_configs, atexit_mock):
    assert mock_metrics_client.configs is mock_cli_user_configs
    assert mock_metrics_client.session_id == mock_cli_user_configs.anon_session_id
    assert mock_metrics_client.posthog.disabled is not mock_cli_user_configs.is_metrics_enabled
    atexit_mock.assert_called_with(mock_metrics_client.pool.shutdown)


def test_platform_info(mock_metrics_client):
    platform_info = mock_metrics_client.platform_info
    assert "platform" in platform_info
    assert "platform_release" in platform_info
    assert "python_version" in platform_info
    assert "codegen_version" in platform_info


def test_capture_event(mock_metrics_client, mock_posthog):
    with patch.object(mock_metrics_client, "platform_info", {"platform": "test_platform"}):
        mock_metrics_client.capture_event("test_event", {"key": "value"})
        mock_metrics_client.pool.submit.assert_called_once()
        mock_metrics_client.pool.submit.assert_called_once_with(
            mock_posthog.capture,
            distinct_id=mock_metrics_client.session_id,
            event="test_event",
            properties={"key": "value", "platform": "test_platform"},
            groups={"platform": "cli"},
        )


def test_capture_event_exception(mock_metrics_client, mock_posthog):
    mock_metrics_client.pool.submit.side_effect = Exception("test exception")
    with patch("src.codegen.cli.metrics.client.global_env.DEBUG", True):
        with patch("src.codegen.cli.metrics.client.traceback.print_exc") as mock_print_exc:
            mock_metrics_client.capture_event("test_event", {"key": "value"})
            mock_print_exc.assert_called_once()
