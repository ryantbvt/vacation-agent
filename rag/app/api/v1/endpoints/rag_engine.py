'''
RAG Engine API
'''

from fastapi import APIRouter, HTTPException
from python_utils.logging.logging import init_logger

from app.modules.google_integration import read_google_sheets

# Initialize logger and FastAPI
logger = init_logger()
router = APIRouter()

# Initialize RAG configs
# TODO

''' API Endpoints'''
@router.post("/sync")
async def sync_data():
    '''
    Description: Sync data from Google Sheets to Vectorized DB

    Args:
        TODO
    
    Returns:
        TODO
    '''
    # Connect to Google Sheets
    title = await read_google_sheets()
    return {"message": f"{title} doc is synced"}