from fastapi import FastAPI
from python_utils.logging.logging import init_logger

logger = init_logger(__name__)

app = FastAPI()

@app.get("/")
def read_root():
    logger.info("Hello World")
    return {"message": "Hello World"}