from pathlib import Path

# Config file
CODEGEN_REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
CODEGEN_DIR_NAME = ".codegen"
CONFIG_FILENAME = "config.toml"
CONFIG_PATH = CODEGEN_REPO_ROOT / CODEGEN_DIR_NAME / CONFIG_FILENAME

# Environment variables
ENV_FILENAME = ".env"
ENV_PATH = CODEGEN_REPO_ROOT / "src" / "codegen" / ENV_FILENAME
