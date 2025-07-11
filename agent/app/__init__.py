''' Initialize configurations for the service '''

from app.schemas.config import AgentConfig
from app import paths

agent_config = AgentConfig.from_yaml(paths.SERVICE_CONFIG_PATH) 