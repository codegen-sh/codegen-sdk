from graph_sitter.core.plugins.axios import AxiosApiFinder
from graph_sitter.core.plugins.flask import FlaskApiFinder
from graph_sitter.core.plugins.modal import ModalApiFinder

PLUGINS = [
    FlaskApiFinder(),
    AxiosApiFinder(),
    ModalApiFinder(),
]
