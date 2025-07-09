''' Embedding API Endpoints '''

import os
from dotenv import load_dotenv

from fastapi import APIRouter
from openai import OpenAI

from python_utils.logging.logging import init_logger
from app.schemas.gateway import EmbeddingRequest, EmbeddingResponse

# Initialize logger
logger = init_logger()
router = APIRouter()

# Initialize keys
try:
    load_dotenv()
except ImportError:
    logger.warning("Tried to load dotenv. Failed. Hopefully running in k8s.")
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

''' API Endpoints '''

@router.post('/embeddings')
async def embeddings(request: EmbeddingRequest) -> EmbeddingResponse:
    '''
    Description: Generate embeddings for a given text

    Args:
        request (EmbeddingRequest): Request that'll be sent to the embedding model

    Returns:
        embedding_response (EmbeddingResponse): Returns the embedding response
    '''

    # Initialize OpenAI client
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

    # Generate embeddings
    embedding_response = openai_client.embeddings.create(
        input=request.text,
        model=request.model_name
    )

    return EmbeddingResponse(embedding=embedding_response.data[0].embedding)