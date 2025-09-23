import pandas as pd
import pathlib

# Project root directory
BASE_DIR = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_DIR / "data"

# List of files to convert
files_to_convert = [
    "abilities.xlsx",
    "interests.xlsx",
    "knowledge.xlsx",
    "occupations.xlsx",
    "skills.xlsx"
]

def convert_excel_to_parquet():
    """Reads Excel files from the data directory and saves them as Parquet files."""
    print("Starting conversion from Excel to Parquet...")
    
    for file_name in files_to_convert:
        excel_path = DATA_PATH / file_name
        parquet_path = DATA_PATH / file_name.replace(".xlsx", ".parquet")

        if not excel_path.exists():
            print(f"Warning: {excel_path} not found. Skipping.")
            continue

        try:
            # Read the Excel file
            df = pd.read_excel(excel_path)
            
            # Save as Parquet
            df.to_parquet(parquet_path, index=False)
            
            print(f"Successfully converted {excel_path} to {parquet_path}")
        except Exception as e:
            print(f"Failed to convert {file_name}. Error: {e}")

if __name__ == "__main__":
    convert_excel_to_parquet()