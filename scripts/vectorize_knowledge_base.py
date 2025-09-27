import pathlib
import json
import chromadb
from sentence_transformers import SentenceTransformer

# File paths
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
ONET_KNOWLEDGE_BASE_FILE_PATH = PROJECT_ROOT / "data" / "onet_knowledge_base.json"
CHROMA_DB_PATH = PROJECT_ROOT / "data" / "chroma_db"


def vectorize_and_store():
    """
    Reads the knowledge base, converts texts to vectors, and stores them in ChromaDB.
    """
    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))

    collection_name = "onet_data"
    existing_collections = {col.name for col in client.list_collections()}
    if collection_name in existing_collections:
        client.delete_collection(collection_name)
    collection = client.create_collection(collection_name)

    model_name = "all-MiniLM-L6-v2"
    embedding_model = SentenceTransformer(model_name)

    knowledge_base_file = ONET_KNOWLEDGE_BASE_FILE_PATH
    try:
        with open(knowledge_base_file, "r", encoding="utf-8") as f:
            documents = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Knowledge base file not found at '{knowledge_base_file}'.")
        print("Please run 'onet_knowledge_base.py' first.")
        return

    doc_contents = [doc["content"] for doc in documents]
    doc_ids = [doc["doc_id"] for doc in documents]
    titles = [doc["title"] for doc in documents]
    vectors = embedding_model.encode(doc_contents).tolist()

    metadatas = [{"title": title} for title in titles]
    collection.add(ids=doc_ids, documents=doc_contents, metadatas=metadatas, embeddings=vectors)
    print(f"Inserted {len(documents)} documents into ChromaDB.")


if __name__ == "__main__":
    vectorize_and_store()