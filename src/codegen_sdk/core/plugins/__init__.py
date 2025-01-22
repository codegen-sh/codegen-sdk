from codegen_sdk.core.plugins.axios import AxiosApiFinder
from codegen_sdk.core.plugins.flask import FlaskApiFinder
from codegen_sdk.core.plugins.modal import ModalApiFinder

PLUGINS = [
    FlaskApiFinder(),
    AxiosApiFinder(),
    ModalApiFinder(),
]
