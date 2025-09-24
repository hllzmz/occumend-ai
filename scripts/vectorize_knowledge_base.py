import pathlib
import json
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType
from sentence_transformers import SentenceTransformer

# File paths
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent 
ONET_KNOWLEDGE_BASE_FILE_PATH = PROJECT_ROOT / "data" / "onet_knowledge_base.json"
MILVUS_DB_PATH = PROJECT_ROOT / "data" / "milvus.db"

def vectorize_and_store():
    """
    Reads the knowledge base, converts texts to vectors, and
    stores them persistently in ChromaDB.
    """

    # Connect to Milvus
    connections.connect(uri=str(MILVUS_DB_PATH))
    # Initialize embedding model
    model_name = "all-MiniLM-L6-v2"
    embedding_model = SentenceTransformer(model_name)

    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
    ]
    schema = CollectionSchema(fields, description="O*NET knowledge base")

    # Create or get collection
    collection_name = "onet_data"
    try:
        collection = Collection(collection_name)
        collection.drop()
    except:
        pass
    collection = Collection(collection_name, schema)

    # Load knowledge base
    knowledge_base_file = ONET_KNOWLEDGE_BASE_FILE_PATH
    try:
        with open(knowledge_base_file, "r", encoding="utf-8") as f:
            documents = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Knowledge base file not found at '{knowledge_base_file}'.")
        print("Please run 'onet_knowledge_base.py' first.")
        return

    # Prepare data for insertion
    doc_contents = [doc["content"] for doc in documents]
    doc_ids = [doc["doc_id"] for doc in documents]
    titles = [doc["title"] for doc in documents]
    vectors = embedding_model.encode(doc_contents).tolist()
    # Insert data into Milvus collection
    entities = [doc_ids, vectors, titles]
    collection.insert(entities)
    collection.create_index(field_name="vector", index_params={"metric_type": "COSINE", "index_type": "FLAT"})
    collection.load()
    print(f"Inserted {len(documents)} documents into Milvus Lite.")

if __name__ == "__main__":
    vectorize_and_store()
