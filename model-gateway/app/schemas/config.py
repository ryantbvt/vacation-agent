''' Gateway Configurations '''

import yaml
from pydantic import BaseModel
from typing import Dict, Optional
from python_utils.logging.logging import init_logger

# Initialize logger
logger = init_logger()

class LLMModels(BaseModel):
    vendor: str
    enabled: bool

class GatewayConfig(BaseModel):
    slm_models: Dict[str, str]
    llm_models: Dict[str, LLMModels]

    @classmethod
    def from_yaml(cls, file: str) -> 'GatewayConfig':
        with open(file, "r") as f:
            config_dict = yaml.safe_load(f)
        return cls.model_validate(config_dict)
    
    @classmethod
    def get_vendor(cls, llm_models: Dict[str, LLMModels], model_name: str) -> str:
        '''
        Description: Get the vendor for a specified model name

        Args:
            model_name: the model we want to find the vendor for

        Return:
            vendor: the vendor for the model
        '''
        logger.info(f'Fetching vendor for model {model_name}')
        try:
            model = llm_models.get(model_name)
            if model is None:
                logger.error(f'Model {model_name} not found in llm_models')
                raise ValueError(f'Model {model_name} not found')
            
            vendor = model.vendor
            
            logger.info(f'Vendor for model {model_name} found. Returning vendor')
            return vendor
        
        except AttributeError as e:
            logger.error(f'Error accessing vendor attribute: {e}')
            raise
        except Exception as e:
            logger.error(f'An unexpected error occurred: {e}')
            raise
