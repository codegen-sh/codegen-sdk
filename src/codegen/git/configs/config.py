import os


class Config:
    def __init__(self) -> None:
        self.ENV = os.environ.get("ENV", "sandbox")
        self.GITHUB_ENTERPRISE_URL = self._get_env_var("GITHUB_ENTERPRISE_URL")
        self.LOWSIDE_TOKEN = self._get_env_var("LOWSIDE_TOKEN")
        self.HIGHSIDE_TOKEN = self._get_env_var("HIGHSIDE_TOKEN")

    def _get_env_var(self, var_name, required: bool = False) -> str | None:
        value = os.environ.get(var_name)
        if value:
            return value
        if required:
            msg = f"Environment variable {var_name} is not set with ENV={self.ENV}!"
            raise ValueError(msg)
        return None


config = Config()
