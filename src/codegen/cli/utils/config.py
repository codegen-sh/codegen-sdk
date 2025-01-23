from pathlib import Path

import toml
from pydantic import BaseModel


class Config(BaseModel):
    repo_name: str = ""
    organization_name: str = ""
    programming_language: str | None = None

    @property
    def repo_full_name(self) -> str:
        return f"{self.organization_name}/{self.repo_name}"


CONFIG_PATH = "config.toml"


def read_model[T: BaseModel](model: type[T], path: Path) -> T:
    if not path.exists():
        return model()
    return model.model_validate(toml.load(path))


def get_config(codegen_dir: Path) -> Config:
    config_path = codegen_dir / CONFIG_PATH
    return read_model(Config, config_path)


def write_model(model: BaseModel, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        toml.dump(model.model_dump(), f)


def write_config(config: Config, codegen_dir: Path) -> None:
    config_path = codegen_dir / CONFIG_PATH
    write_model(config, config_path)
