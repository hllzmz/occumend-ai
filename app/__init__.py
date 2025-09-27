from flask import Flask
from .config import Config
from .data_processing import load_and_prepare_data
import openai
import chromadb
from sentence_transformers import SentenceTransformer


def create_app(config_class=Config):
    """Application Factory: Creates and configures the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    with app.app_context():
        # Load initial data
        (
            app.df_clustered_jobs,
            app.knowledge_map,
            app.skills_map,
            app.abilities_map,
        ) = load_and_prepare_data(app.config)

        if app.df_clustered_jobs is None:
            print("Critical Error: Data could not be loaded, server cannot start.")

        # Initialize service clients
        # Initialize LLM client
        try:
            if not app.config["OPEN_ROUTER_API_KEY"]:
                app.llm_client = None
                print("Warning: OPEN_ROUTER_API_KEY is not set.")
            else:
                print(f"DEBUG: Attempting to initialize LLM client with key length: {len(app.config['OPEN_ROUTER_API_KEY'])}")
                app.llm_client = openai.OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=app.config["OPEN_ROUTER_API_KEY"],
                )
                print("DEBUG: LLM Client initialized successfully.")
        except Exception as e:
            app.llm_client = None
            print(f"CRITICAL LLM ERROR: Failed to initialize OpenAI client: {e}")

        # Initialize RAG components
        try:
            chroma_path = app.config["VECTOR_DB_PATH"]
            app.chroma_client = chromadb.PersistentClient(path=str(chroma_path))
            print("DEBUG: ChromaDB connection established.")

            app.embedding_model = SentenceTransformer(app.config["EMBEDDING_MODEL_NAME"])
            print(f"DEBUG: Embedding model '{app.config['EMBEDDING_MODEL_NAME']}' loaded.")

            app.onet_collection = app.chroma_client.get_collection(app.config["ONET_COLLECTION_NAME"])
            print(f"DEBUG: Collection '{app.config['ONET_COLLECTION_NAME']}' loaded successfully.")

        except Exception as e:
            print(f"CRITICAL RAG INIT ERROR: RAG components could not be fully initialized. ERROR: {e}")
            app.onet_collection = None
            app.chroma_client = None

    # Register routes
    from . import routes

    app.register_blueprint(routes.bp)

    return app
