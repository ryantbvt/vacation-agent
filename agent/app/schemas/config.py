from pydantic import BaseModel
import yaml
from pathlib import Path

class AgentConfig(BaseModel):
    pass

    @classmethod
    def from_yaml(cls, config_path: Path):
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data['agent']) 