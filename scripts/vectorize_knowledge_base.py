import pathlib
import json
import chromadb
from chromadb.utils import embedding_functions

# File paths
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent 
ONET_KNOWLEDGE_BASE_FILE_PATH = PROJECT_ROOT / "data" / "onet_knowledge_base.json"
CHROMA_DB_PATH = PROJECT_ROOT / "chroma_db"

def vectorize_and_store():
    """
    Reads the knowledge base, converts texts to vectors, and
    stores them persistently in ChromaDB.
    """

    # Model and database client
    model_name = "all-MiniLM-L6-v2"
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name
    )

    # Persist the database in a folder named 'chroma_db'
    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))

    # Create (or use if exists) a collection named 'onet_data'
    collection_name = "onet_data"
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=sentence_transformer_ef,
        metadata={"hnsw:space": "cosine"},
    )

    # Load the knowledge base file
    knowledge_base_file = ONET_KNOWLEDGE_BASE_FILE_PATH
    try:
        with open(knowledge_base_file, "r", encoding="utf-8") as f:
            documents = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Knowledge base file not found at '{knowledge_base_file}'.")
        print("Please run 'onet_knowledge_base.py' first.")
        return

    # Add data to ChromaDB
    if collection.count() > 0:
        existing_ids = collection.get(include=[])["ids"]
        if existing_ids:
            collection.delete(ids=existing_ids)
            print(f"Deleted {len(existing_ids)} old documents from the collection.")

    # Prepare documents, metadata, and IDs as lists
    doc_contents = [doc["content"] for doc in documents]
    doc_ids = [doc["doc_id"] for doc in documents]
    metadatas = [{"title": doc["title"]} for doc in documents]

    batch_size = 100
    for i in range(0, len(doc_contents), batch_size):
        batch_docs = doc_contents[i : i + batch_size]
        batch_ids = doc_ids[i : i + batch_size]
        batch_metas = metadatas[i : i + batch_size]

        collection.add(documents=batch_docs, metadatas=batch_metas, ids=batch_ids)
        print(
            f"  Processed batch {i//batch_size + 1}/{(len(doc_contents)-1)//batch_size + 1}..."
        )

if __name__ == "__main__":
    vectorize_and_store()
