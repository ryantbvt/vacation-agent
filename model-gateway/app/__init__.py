''' Initialize configurations for the service '''

from app.schemas.config import GatewayConfig
from app import paths

gateway_config = GatewayConfig.from_yaml(paths.SERVICE_CONFIG_PATH)