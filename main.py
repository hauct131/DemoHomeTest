"""
Entry point chính cho OptiSigns RAG Pipeline.

Cách chạy:
    python main.py
"""

import sys
from pathlib import Path

# Thêm project root vào sys.path để import src/
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.pipeline import run_pipeline
from src import config


def main():
    """Chạy toàn bộ pipeline."""
    try:
        stats = run_pipeline(
            input_json=config.INPUT_JSON_PATH,
            output_docs=config.OUTPUT_DOCS_PATH,
            output_chunks=config.OUTPUT_CHUNKS_PATH,
            output_audit=config.OUTPUT_AUDIT_PATH,
            verbose=True,
        )
        
        # Exit code 0 = success
        sys.exit(0)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
