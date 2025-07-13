import yaml

from pydantic import BaseModel

from app.schemas.intent_config import IntentSkill

class AgentConfig(BaseModel):
    intent_skills: IntentSkill

    @classmethod
    def from_yaml(cls, file: str):
        with open(file, 'r') as f:
            config_dict = yaml.safe_load(f)
        return cls.model_validate(config_dict)