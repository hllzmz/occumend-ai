from flask import Flask
from .config import Config
from .data_processing import load_and_prepare_data
import openai
import chromadb
from chromadb.utils import embedding_functions


def create_app(config_class=Config):
    """Application Factory: Creates and configures the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    with app.app_context():
        # Load initial data and make it accessible application-wide
        (
            app.df_clustered_jobs,
            app.knowledge_map,
            app.skills_map,
            app.abilities_map,
        ) = load_and_prepare_data(app.config)

        if app.df_clustered_jobs is None:
            print("Critical Error: Data could not be loaded, server cannot start.")

        # Initialize service clients
        try:
            if not app.config["OPEN_ROUTER_API_KEY"]:
                app.llm_client = None
                print(
                    "Warning: OPEN_ROUTER_API_KEY is not set. Chat feature will not work."
                )
            else:
                app.llm_client = openai.OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=app.config["OPEN_ROUTER_API_KEY"],
                )

            chroma_client = chromadb.PersistentClient(
                path=str(app.config["CHROMA_DB_PATH"])
            )
            sentence_transformer_ef = (
                embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=app.config["EMBEDDING_MODEL_NAME"]
                )
            )
            app.onet_collection = chroma_client.get_collection(
                name=app.config["ONET_COLLECTION_NAME"],
                embedding_function=sentence_transformer_ef,
            )
        except Exception as e:
            print(f"Error: RAG components could not be initialized: {e}")
            app.llm_client = None
            app.onet_collection = None

    # Register routes (Blueprint)
    from . import routes

    app.register_blueprint(routes.bp)

    return app
