import pathlib
import json
import lancedb
from sentence_transformers import SentenceTransformer

# File paths
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
ONET_KNOWLEDGE_BASE_FILE_PATH = PROJECT_ROOT / "data" / "onet_knowledge_base.json"
LANCE_DB_PATH = PROJECT_ROOT / "data" / "lancedb_store"


def vectorize_and_store():
    """
    Reads the knowledge base, converts texts to vectors, and stores them in LanceDB.
    """
    knowledge_base_file = ONET_KNOWLEDGE_BASE_FILE_PATH
    try:
        with open(knowledge_base_file, "r", encoding="utf-8") as f:
            documents = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Knowledge base file not found at '{knowledge_base_file}'.")
        print("Please run 'onet_knowledge_base.py' first.")
        return

    model_name = "all-MiniLM-L6-v2"
    embedding_model = SentenceTransformer(model_name)

    doc_contents = [doc["content"] for doc in documents]
    doc_ids = [doc["doc_id"] for doc in documents]
    titles = [doc["title"] for doc in documents]
    vectors = embedding_model.encode(doc_contents)

    LANCE_DB_PATH.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(str(LANCE_DB_PATH))

    table_name = "onet_data"
    if table_name in db.table_names():
        db.drop_table(table_name)

    records = []
    for doc_id, title, content, vector in zip(doc_ids, titles, doc_contents, vectors):
        records.append(
            {
                "doc_id": doc_id,
                "title": title,
                "content": content,
                "embedding": vector.tolist(),
            }
        )

    db.create_table(table_name, data=records, mode="overwrite")
    print(f"Inserted {len(records)} documents into LanceDB at '{LANCE_DB_PATH}'.")


if __name__ == "__main__":
    vectorize_and_store()