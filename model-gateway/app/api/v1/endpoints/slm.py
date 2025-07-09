''' Gateway for Small Language Models (SLM) '''

from fastapi import APIRouter, HTTPException
from python_utils.logging.logging import init_logger
from typing import Dict
import httpx

from app import gateway_config
from app.schemas.gateway import GatewayRequest

# Initialize logger and FastAPI
logger = init_logger()
router = APIRouter()

# initialize configs
slm_models = gateway_config.slm_models

''' API '''

# TODO: Add SLMs and see if there's some sort of standardized response, otherwise keep Dict as the norm

@router.post('/predict')
async def predict(request: GatewayRequest) -> Dict:
    '''
    Description: Forwards requests to SLM

    Args:
        request: Request that'll be sent to the SLM

    Returns:
        slm_response (Any): returns any response due to different SLMs have different return types
    '''
    logger.info(f"Request received. Model: {request.model_name}")

    # fetch endpoint and verify valid model
    endpoint = f"{slm_models.get(request.model_name)}/v1/analyze"
    logger.info(f"Sending SLM request to: {endpoint}")
    if not endpoint:
        logger.error(f"Model, {request.model_name}, not found")
        raise HTTPException(status_code=400, detail="Model not found")
    
    # Build payload
    request_payload = {
        "prompt": request.prompt
    }

    # Send request to model
    try:
        async with httpx.AsyncClient() as client:
            slm_response = await client.post(
                url=endpoint,
                json=request_payload
            )
            slm_response.raise_for_status()
            logger.info(f"Request to {endpoint} was successful.")
            
            return slm_response.json()

    except Exception as e:
        logger.error(f"Error occured: {e}")
        raise HTTPException(status_code=500, detail="SLM Prediction Server Error")
