'''
Pinecone Database Operations
'''

import os
import datetime
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from python_utils.logging.logging import init_logger

# Initialize logger
logger = init_logger()

class PineconeManager:
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
    
    def get_existing_vectors(self, limit: int = 10000):
        """Fetch existing vectors from the index"""
        existing_vectors = {}
        try:
            # Fetch existing vectors (you might want to implement pagination for large datasets)
            fetch_response = self.index.query(
                vector=[0] * 1536,  # Dummy vector to get all vectors
                top_k=limit,
                include_metadata=True
            )
            for match in fetch_response.matches:
                existing_vectors[match.id] = match.metadata
            logger.debug(f"Fetched {len(existing_vectors)} existing vectors")
        except Exception as e:
            logger.warning(f"Could not fetch existing vectors: {e}")
        
        return existing_vectors
    
    def prepare_vectors(self, sheet_data, embeddings):
        """Prepare vectors for upload with metadata"""
        vectors_to_upsert = []
        new_count = 0
        update_count = 0
        
        # Get existing vectors for update detection
        existing_vectors = self.get_existing_vectors()
        
        for i, (row, embedding) in enumerate(zip(sheet_data, embeddings)):
            # Create a unique ID based on content hash for better update detection
            content_hash = hash(row.content) % 1000000
            vector_id = f"content_{content_hash}"
            
            # Prepare metadata with timestamp and version info
            metadata = {
                "content": row.content,
                "row_index": i,
                "source": "google_sheets",
                "last_updated": str(datetime.datetime.now()),
                "content_hash": content_hash,
                "sync_version": "1.0"  # Increment this when you change the sync logic
            }
            
            # Add any additional fields from your Google Sheets data
            if hasattr(row, 'title'):
                metadata["title"] = row.title
            if hasattr(row, 'category'):
                metadata["category"] = row.category
            
            # Check if this is a new vector or an update
            is_update = vector_id in existing_vectors
            if is_update:
                update_count += 1
                logger.debug(f"Updating existing vector: {vector_id}")
            else:
                new_count += 1
                logger.debug(f"Adding new vector: {vector_id}")
            
            vectors_to_upsert.append({
                "id": vector_id,
                "values": embedding,
                "metadata": metadata
            })
        
        return vectors_to_upsert, new_count, update_count
    
    def upload_vectors(self, vectors_to_upsert, batch_size: int = 100):
        """Upload vectors to Pinecone in batches"""
        try:
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                self.index.upsert(vectors=batch)
                logger.info(f"Uploaded batch {i//batch_size + 1} of {(len(vectors_to_upsert) + batch_size - 1)//batch_size}")
            
            logger.info(f"Successfully uploaded {len(vectors_to_upsert)} vectors to Pinecone")
            return True
        except Exception as e:
            logger.error(f"Error uploading to Pinecone: {e}")
            raise e
    
    def sync_data(self, sheet_data, embeddings):
        """Complete sync operation: prepare and upload vectors"""
        try:
            # Prepare vectors for upload
            vectors_to_upsert, new_count, update_count = self.prepare_vectors(sheet_data, embeddings)
            
            # Upload vectors to Pinecone
            self.upload_vectors(vectors_to_upsert)
            
            return {
                "new_vectors": new_count,
                "updated_vectors": update_count,
                "total_vectors": len(vectors_to_upsert)
            }
        except Exception as e:
            logger.error(f"Error in sync operation: {e}")
            raise e 