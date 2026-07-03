import os
import sys
from pathlib import Path

# Thêm project root vào sys.path để import src/
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from scripts.crawl import run_crawl
from src.pipeline import run_pipeline
from src import config
from scripts.upload_vector_store import run_upload


def main():
    """Chạy toàn bộ pipeline (Scrape -> Parse -> Chunk -> Audit -> Upload)."""
    # Load environment variables
    load_dotenv()

    # Map API_KEY env var (từ Docker) sang OPENAI_API_KEY
    if "API_KEY" in os.environ and not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = os.environ["API_KEY"]

    try:
        # 0. Re-scrape Zendesk Help Center -> ghi đè data/optisigns_articles.json
        #    Bước bắt buộc để job hàng ngày phát hiện bài viết mới/cập nhật;
        #    nếu bỏ qua, pipeline sẽ luôn xử lý lại data cũ.
        try:
            run_crawl(verbose=True)
        except Exception as e:
            print(f"[main] Cảnh báo: Re-scrape thất bại ({e}). "
                  f"Sẽ dùng lại data/optisigns_articles.json hiện có nếu tồn tại.")

        # 1. Chạy Parsing, Cleaning, Chunking và Auditing (Phase 1)
        stats = run_pipeline(
            input_json=config.INPUT_JSON_PATH,
            output_docs=config.OUTPUT_DOCS_PATH,
            output_chunks=config.OUTPUT_CHUNKS_PATH,
            output_audit=config.OUTPUT_AUDIT_PATH,
            verbose=True,
        )
        
        # 2. Chạy Vector Store upload (Phase 2 & 3 delta uploader)
        # Chỉ chạy nếu có API key
        if os.environ.get("OPENAI_API_KEY"):
            print("\n[main] Phát hiện API Key, bắt đầu đồng bộ lên OpenAI Vector Store...")
            run_upload(
                dry_run=False,
                force=False,
                chunks_path=str(config.OUTPUT_CHUNKS_PATH),
                max_workers=8,
            )
        else:
            print("\n[main] Không tìm thấy OPENAI_API_KEY hoặc API_KEY trong môi trường. Bỏ qua bước upload.")
        
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