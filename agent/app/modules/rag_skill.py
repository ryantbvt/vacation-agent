''' RAG Skill '''

import os
from dotenv import load_dotenv

from pinecone import Pinecone, ServerlessSpec
from python_utils.logging.logging import init_logger

from app.schemas.agent import ChatResponse
from app.schemas.rag_skill import RagSkillConfig

# Initialize logger
logger = init_logger()

class RAGSkill:
    def __init__(self, index_name: str = "rag-engine"):
        self.index_name = index_name
        self.pinecone_db = None
        self.index = None
        self._initialize_pinecone()
    
    def _initialize_pinecone(self):
        """Initialize Pinecone connection and create index if needed"""
        # Initialize Pinecone API key
        try:
            load_dotenv()
        except ImportError:
            logger.warning("Tried to load dotenv. Failed. Hopefully running in k8s.")
        
        PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
        
        if PINECONE_API_KEY is None:
            logger.error('Missing Pinecone API key')
            raise ValueError("Missing Pinecone API key. Please set PINECONE_API_KEY variable.")
        
        # Initialize Pinecone
        self.pinecone_db = Pinecone(api_key=PINECONE_API_KEY)
        
        # Create index if it doesn't exist
        if self.index_name not in self.pinecone_db.list_indexes().names():
            logger.info(f"Creating Pinecone index: {self.index_name}")
            self.pinecone_db.create_index(
                name=self.index_name,
                dimension=1536,  # 1536 for text-embedding-3-small, 3072 for text-embedding-3-large
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            logger.info(f"Successfully created Pinecone index: {self.index_name}")
        
        # Get the index
        self.index = self.pinecone_db.Index(self.index_name)
        logger.info(f"Connected to Pinecone index: {self.index_name}")

    def query_index(self, user_query: str) -> str:
        '''
        Description: Querying the Pinecone DB for most relevent chunks.

        Args:
            user_query (str): The user's query

        Returns:
            chunks (list[str]): The most relevant chunks
        '''
        pass

    def generate_response(self, user_query: str) -> ChatResponse:
        '''
        Description: Generating a response using the LLM.

        Args:
            user_query (str): The user's query

        Returns:
            response (ChatResponse): The response for RagSkill
        '''
        # Step 1: Get chunks from Pinecone DB
        chunks = self.query_index(user_query)
        logger.info(f"Found {len(chunks)} chunks")

        # Step 2: Send to LLM
        llm_request = {
            "model": config.rag_skill.model,
        }

        return response