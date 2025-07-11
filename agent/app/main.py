from fastapi import FastAPI
from python_utils.logging.logging import init_logger

from app.api.v1.router import api_router

# Initialize loger
logger = init_logger()

logger.info('Starting application...')

# Intialize FastAPI
app = FastAPI()

# Connect routers to main application
app.include_router(api_router, prefix="/v1")
