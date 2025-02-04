from unittest.mock import MagicMock, patch

import pytest

from codegen.cli.config import CLIUserConfigs
from codegen.cli.metrics.client import MetricsClient, get_metrics_client


@pytest.fixture(autouse=True)
def mock_metrics_client():
    get_metrics_client.cache_clear()
    client_mock = MagicMock(spec=MetricsClient)
    with patch("codegen.cli.metrics.client.MetricsClient", return_value=client_mock):
        yield get_metrics_client()


@pytest.fixture(autouse=True)
def mock_cli_user_configs():
    with patch("src.codegen.cli.config.CONFIG_PATH") as mock:
        configs = CLIUserConfigs(is_metrics_enabled=False)
        with patch.object(CLIUserConfigs, "load", return_value=configs):
            yield configs
