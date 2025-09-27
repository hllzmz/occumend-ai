from flask import Flask
from .config import Config
from .data_processing import load_and_prepare_data
import openai
import lancedb
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
            vector_path = (
                app.config.get("VECTOR_DB_PATH")
                or app.config.get("LANCE_DB_PATH")
            )
            if not vector_path:
                raise ValueError("VECTOR_DB_PATH is not configured.")

            app.lancedb_client = lancedb.connect(str(vector_path))
            print(f"DEBUG: LanceDB connection established at '{vector_path}'.")

            app.embedding_model = SentenceTransformer(app.config["EMBEDDING_MODEL_NAME"])
            print(f"DEBUG: Embedding model '{app.config['EMBEDDING_MODEL_NAME']}' loaded.")

            table_name = app.config["ONET_COLLECTION_NAME"]
            if table_name not in app.lancedb_client.table_names():
                raise ValueError(f"Table '{table_name}' not found in LanceDB store.")

            app.onet_collection = app.lancedb_client.open_table(table_name)
            app.vector_store = app.lancedb_client
            print(f"DEBUG: Table '{table_name}' loaded successfully from LanceDB.")

        except Exception as e:
            print(f"CRITICAL RAG INIT ERROR: RAG components could not be fully initialized. ERROR: {e}")
            app.onet_collection = None
            app.lancedb_client = None
            app.vector_store = None

    # Register routes
    from . import routes

    app.register_blueprint(routes.bp)

    return app
