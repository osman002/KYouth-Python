import sys
from pathlib import Path 
from src.ingestor import ingest_all_mhtml
from src.processor import process_all_html

SOURCE_DIR = Path("data/0_source")
BRONZE_DIR = Path("data/1_bronze")
SILVER_DIR = Path("data/2_silver")

def run_bronze():
    input_dir = SOURCE_DIR
    output_dir = BRONZE_DIR
    ingest_all_mhtml(input_dir, output_dir)

def run_silver():
    input_dir = BRONZE_DIR
    output_dir = SILVER_DIR
    process_all_html(input_dir, output_dir)

def main():
    print("Hello from learning!")

if __name__ == "__main__":
    match sys.argv[1] if len(sys.argv) > 1 else "":
        case "ingest":
            run_bronze()
        case "process":
            run_silver()
        case _:
            print("Unknown command. Available commands: ingest")
