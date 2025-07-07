import os
from pathlib import Path

_ROOT_DIR = Path(os.path.abspath(__file__)).parent

# Service config
SERVICE_CONFIG_DIR = _ROOT_DIR / "configs/config.yaml"
SERVICE_CONFIG_PATH = Path(os.environ.get("SERVICE_CONFIG_PATH", str(SERVICE_CONFIG_DIR)))