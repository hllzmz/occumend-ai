import os
import pathlib
from dotenv import load_dotenv

# Project root directory /app 
BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()

load_dotenv(dotenv_path=BASE_DIR / ".env") 


# Load environment variables from .env file if it exists
class Config:
    """Contains configuration settings for the application."""
    # API Keys
    OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
    #OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Model Settings
    LLM_CHAT_MODEL = "openai/gpt-oss-20b:free"
    #LLM_CHAT_MODEL = "gpt-4o"

    # Embedding model for vector db
    EMBEDDING_MODEL_NAME = "models/all-MiniLM-L6-v2"

    # Data and chromadb directories 
    DATA_PATH = BASE_DIR / "data"
    MILVUS_DB_PATH = BASE_DIR / "data" / "milvus.db"

    ONET_COLLECTION_NAME = "onet_data"

    # File Paths
    ABILITIES_FILE_PATH = DATA_PATH / "abilities.parquet"
    INTERESTS_FILE_PATH = DATA_PATH / "interests.parquet"
    KNOWLEDGE_FILE_PATH = DATA_PATH / "knowledge.parquet"
    OCCUPATIONS_FILE_PATH = DATA_PATH / "occupations.parquet"
    SKILLS_FILE_PATH = DATA_PATH / "skills.parquet"