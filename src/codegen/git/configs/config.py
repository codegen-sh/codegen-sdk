import os




class Config:
    def __init__(self) -> None:
        self.GITHUB_TOKEN = self._get_env_var("GITHUB_TOKEN")

    def _get_env_var(self, var_name, required: bool = False) -> str | None:
        value = os.environ.get(var_name)
        if value:
            return value
        if required:
            msg = f"Environment variable {var_name} is not set!"
            raise ValueError(msg)
        return None


config = Config()
