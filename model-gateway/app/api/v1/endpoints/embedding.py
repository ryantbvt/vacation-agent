''' Embedding API Endpoints '''

import os
from dotenv import load_dotenv

from fastapi import APIRouter
from openai import OpenAI

from python_utils.logging.logging import init_logger
from app.schemas.gateway import EmbeddingRequest, EmbeddingResponse, BatchEmbeddingRequest, BatchEmbeddingResponse

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
    logger.info(f"Generating embeddings. Embedding model: {request.model_name}")
    embedding_response = openai_client.embeddings.create(
        input=request.text,
        model=request.model_name
    )

    logger.info(f"Successfully generated embeddings. Embedding model: {request.model_name}")
    return EmbeddingResponse(embedding=embedding_response.data[0].embedding)

@router.post('/embeddings/batch')
async def batch_embeddings(request: BatchEmbeddingRequest) -> BatchEmbeddingResponse:
    '''
    Description: Generate embeddings for multiple texts in a single request

    Args:
        request (BatchEmbeddingRequest): Request containing multiple texts to embed

    Returns:
        batch_embedding_response (BatchEmbeddingResponse): Returns embeddings for all texts
    '''

    # Initialize OpenAI client
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

    # Generate embeddings for all texts at once
    logger.info(f"Generating batch embeddings for {len(request.texts)} texts. Model: {request.model_name}")
    
    # Validate and clean texts for OpenAI API
    validated_texts = []
    for i, text in enumerate(request.texts):
        if not isinstance(text, str):
            logger.error(f"Text {i} is not a string: {type(text)} - {text}")
            raise ValueError(f"Text {i} must be a string, got {type(text)}")
        # Replace empty/whitespace-only texts with a space to satisfy OpenAI API requirements
        validated_texts.append(text.strip() if text.strip() else " ")
    
    # Send embedding request to OpenAI
    embedding_response = openai_client.embeddings.create(
        input=validated_texts,
        model=request.model_name
    )

    # Extract embeddings from response
    embeddings = [data.embedding for data in embedding_response.data]
    
    logger.info(f"Successfully generated batch embeddings for {len(embeddings)} texts. Model: {request.model_name}")
    return BatchEmbeddingResponse(embeddings=embeddings)