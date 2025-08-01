'''
RAG Engine API
'''

import httpx
from fastapi import APIRouter, HTTPException
from python_utils.logging.logging import init_logger

from app.paths import SERVICE_CONFIG_PATH
from app.modules.google_integration import read_google_sheets
from app.modules.pinecone import PineconeManager
from app.schemas.config import ServiceConfig

# Initialize logger and FastAPI
logger = init_logger()
router = APIRouter()

# Initialize RAG configs
embedding_config = ServiceConfig.from_yaml(SERVICE_CONFIG_PATH).embedding
EMBEDDING_GATEWAY = embedding_config.model_gateway
EMBEDDING_MODEL = embedding_config.model_name

# Initialize Pinecone manager
pinecone_manager = PineconeManager()

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
            # Extract all texts from Google Sheets data
            texts = [row.content for row in google_sheets_data.sheet_data]
            
            # Make a single batch request instead of individual requests
            batch_embedding_request = {
                "texts": texts,
                "model_name": EMBEDDING_MODEL
            }

            embedding_response = await client.post(
                url=f"{EMBEDDING_GATEWAY}/embeddings/batch",
                json=batch_embedding_request
            )
            embedding_response.raise_for_status()
            
            # Get all embeddings from the batch response
            batch_response = embedding_response.json()
            all_embedded_data = batch_response["embeddings"]
    
    except Exception as e:
        logger.error(f"Error embedding data: {e}")
        raise HTTPException(status_code=500, detail="Error embedding request")

    # Sync data to Pinecone DB
    try:
        sync_result = pinecone_manager.sync_data(google_sheets_data.sheet_data, all_embedded_data)
        new_count = sync_result["new_vectors"]
        update_count = sync_result["updated_vectors"]
        total_vectors = sync_result["total_vectors"]
        
        logger.info(f"Successfully synced to Pinecone: {new_count} new vectors, {update_count} updated vectors")
        
    except Exception as e:
        logger.error(f"Error uploading to Pinecone: {e}")
        raise HTTPException(status_code=500, detail="Error uploading to Pinecone")

    return {
        "message": f"Successfully synced {len(google_sheets_data.sheet_data)} documents to Pinecone",
        "new_vectors": new_count,
        "updated_vectors": update_count,
        "total_vectors": total_vectors
    }