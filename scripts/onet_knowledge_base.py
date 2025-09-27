import pandas as pd
import json
import re
import pathlib

# File paths
PROJECT_ROOT = pathlib.Path(__file__).parents[1].resolve()
DATA_DIR = PROJECT_ROOT / "data"

OCCUPATIONS_FILE_PATH = DATA_DIR / "occupations.xlsx"
TASKS_STATEMENTS_FILE_PATH = DATA_DIR / "task_statements.xlsx"
WORK_CONTEXT_FILE_PATH = DATA_DIR / "work_context.xlsx"

datafromdb = pd.read_excel(WORK_CONTEXT_FILE_PATH)


def clean_text(text):
    """Clean special characters (basic) and extra whitespace in the text."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r"\s+", " ", text) 
    return text.strip()


def chunk_text(text, max_words=200, overlap=40):
    """Split text into overlapping chunks for retrieval."""
    if not isinstance(text, str) or not text.strip():
        return []
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    total_words = len(words)

    while start < total_words:
        end = min(start + max_words, total_words)
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)

        if end >= total_words:
            break

        next_start = max(end - overlap, start + 1)
        start = next_start
    return chunks


def build_knowledge_base():
    """
    Read data from O*NET files, create a combined text document per occupation,
    and save it into a JSON file.
    """
    try:
        # Core occupation data (Title and Description)
        df_occupations = pd.read_excel(
            OCCUPATIONS_FILE_PATH, usecols=["O*NET-SOC Code", "Title", "Description"]
        )
        df_occupations.set_index("O*NET-SOC Code", inplace=True)

        # Tasks
        df_tasks = pd.read_excel(
            TASKS_STATEMENTS_FILE_PATH, usecols=["O*NET-SOC Code", "Task"]
        )
        tasks_dict = (
            df_tasks.groupby("O*NET-SOC Code")["Task"]
            .apply(lambda x: " ".join(f"- {clean_text(t)}" for t in x))
            .to_dict()
        )

        # Work Context
        df_context = pd.read_excel(
            WORK_CONTEXT_FILE_PATH,
            usecols=["O*NET-SOC Code", "Element Name", "Category"],
        )

        # Group by occupation; join unique context element names
        context_dict = (
            df_context.groupby("O*NET-SOC Code")["Element Name"]
            .apply(lambda x: ", ".join(x.unique()))
            .to_dict()
        )

    except FileNotFoundError as e:
        print(f"ERROR: Could not find data file: {e.filename}")
        return

    knowledge_base = []

    for code, row in df_occupations.iterrows():
        title = clean_text(row["Title"])
        description = clean_text(row["Description"])

        # Get tasks
        tasks = tasks_dict.get(code, "No specific tasks listed.")

        # Get work context
        work_context = context_dict.get(code, "No specific work context listed.")

        # Build combined rich text
        combined_text = (
            f"Occupation: {title}\n\n"
            f"Summary: {description}\n\n"
            f"Key Tasks:\n{tasks}\n\n"
            f"Work Environment and Context includes: {work_context}"
        )

        chunks = chunk_text(combined_text, max_words=200, overlap=50)
        if not chunks:
            chunks = [combined_text]

        for idx, chunk in enumerate(chunks, start=1):
            knowledge_base.append(
                {
                    "doc_id": f"{code}#{idx}",
                    "title": f"{title} (Chunk {idx})",
                    "content": chunk,
                }
            )

    output_filename = DATA_DIR / "onet_knowledge_base.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    build_knowledge_base()
