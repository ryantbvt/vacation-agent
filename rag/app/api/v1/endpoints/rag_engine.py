'''
RAG Engine API
'''

import httpx

from fastapi import APIRouter, HTTPException
from python_utils.logging.logging import init_logger

from app.paths import SERVICE_CONFIG_PATH
from app.modules.google_integration import read_google_sheets
from app.schemas.config import ServiceConfig

# Initialize logger and FastAPI
logger = init_logger()
router = APIRouter()

# Initialize RAG configs
embedding_config = ServiceConfig.from_yaml(SERVICE_CONFIG_PATH).embedding
EMBEDDING_GATEWAY = embedding_config.model_gateway
EMBEDDING_MODEL = embedding_config.model_name

''' API Endpoints'''
@router.post("/sync")
async def sync_data():
    '''
    Description: Sync data from Google Sheets to Vectorized DB

    Args:
        None # think about adding spreadsheet id then remove google_sheet config
    
    Returns:
        TODO
    '''
    # Connect to Google Sheets
    google_sheets_data = await read_google_sheets()

    # TODO: Vectorize / Embed the Google Sheets data
    all_embedded_data = []
    
    try:
        async with httpx.AsyncClient() as client:
            for row in google_sheets_data.sheet_data:
                embedding_request = {
                    "text": row.content,
                    "model_name": EMBEDDING_MODEL
                }

                embedding_response = await client.post(
                    url=EMBEDDING_GATEWAY,
                    json=embedding_request
                )
                embedding_response.raise_for_status()
                all_embedded_data.append(embedding_response.json())
    
    except Exception as e:
        logger.error(f"Error embedding data: {e}")
        raise HTTPException(status_code=500, detail="Error embedding request")

    # TODO: Sync data to Pinecone DB


    return {"message": " doc is synced"}