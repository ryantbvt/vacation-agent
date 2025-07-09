''' RAG Engine Configurations '''

import yaml
from pydantic import BaseModel

class GoogleSheetConfig(BaseModel):
    sheet_id: str

class EmbeddingConfig(BaseModel):
    model_gateway: str
    model_name: str

class ServiceConfig(BaseModel):
    google_sheets: GoogleSheetConfig
    embedding: EmbeddingConfig

    @classmethod
    def from_yaml(cls, file: str) -> "ServiceConfig":
        with open(file, "r") as f:
            config_dict = yaml.safe_load(f)
        return cls.model_validate(config_dict)