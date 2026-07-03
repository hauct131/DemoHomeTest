"""
Upload từng chunk (từ chunks.jsonl) lên OpenAI Vector Store, MỖI CHUNK = 1 FILE RIÊNG.

Vì sao làm vậy thay vì upload thẳng 397 file markdown để OpenAI tự chunk:
    - Kiểm soát HOÀN TOÀN nội dung được embed: dùng field `embedding_text` (đã có
      title + heading prefix từ Phase 1) thay vì để OpenAI tự cắt file theo cách
      không biết ngữ cảnh.
    - Chèn dòng "Article URL: <url>" dạng PLAINTEXT vào đầu mỗi file -> khớp
      chính xác với yêu cầu system prompt: 'Cite up to 3 "Article URL:" lines'.
      Nếu chỉ để URL trong metadata, model khó tự sinh đúng format khi trả lời.
    - Mỗi file được set chunking_strategy="static" với max_chunk_size_tokens đủ
      lớn hơn embedding_token_count -> OpenAI KHÔNG cắt lại chunk của mình nữa,
      giữ nguyên ranh giới chunk đã được audit ở Phase 1 (không orphan heading,
      không mid-sentence, không duplicate...).

State file (`vector_store_state.json`) lưu mapping chunk_id -> openai_file_id +
content_hash, dùng để Phase 3 (daily job) biết chunk nào mới/đổi/không đổi mà
không cần re-upload toàn bộ.
"""

import hashlib
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional

from openai import OpenAI

# Buffer trên token_count thực tế của embedding_text, để OpenAI không cắt lại
# chunk đã được chia cẩn thận ở Phase 1. Phải nằm trong khoảng OpenAI cho phép (100-4096).
STATIC_CHUNK_MAX_TOKENS = 800
STATIC_CHUNK_OVERLAP_TOKENS = 0  # Overlap đã được xử lý thủ công lúc pre-chunking

DEFAULT_STATE_PATH = Path("vector_store_state.json")
DEFAULT_CHUNKS_PATH = Path("chunks.jsonl")


# ============================================================
# Đọc dữ liệu & build nội dung file
# ============================================================

def load_chunks(chunks_path: Path = DEFAULT_CHUNKS_PATH) -> List[Dict]:
    """Đọc chunks.jsonl thành list dict."""
    chunks = []
    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks


def build_file_content(chunk: Dict) -> str:
    """
    Build nội dung file sẽ upload lên OpenAI cho 1 chunk.

    Format:
        Article URL: <url gốc>

        <title> — <heading>

        <nội dung chunk>

    Dòng "Article URL:" đứng riêng, plaintext, để model có thể trực tiếp copy
    lại khi trả lời (đúng yêu cầu system prompt "Cite up to 3 Article URL: lines").
    """
    return f"Article URL: {chunk['source_url']}\n\n{chunk['embedding_text']}"


def content_hash(text: str) -> str:
    """Hash nội dung để Phase 3 phát hiện chunk có bị đổi hay không."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_chunk_files(chunks: List[Dict], out_dir: Path) -> Dict[str, Path]:
    """
    Ghi mỗi chunk thành 1 file .md riêng trong out_dir.

    Returns:
        {chunk_id: file_path}
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for c in chunks:
        content = build_file_content(c)
        file_path = out_dir / f"{c['chunk_id']}.md"
        file_path.write_text(content, encoding="utf-8")
        paths[c["chunk_id"]] = file_path
    return paths


# ============================================================
# State management (manifest cho Phase 3 delta upload)
# ============================================================

def load_state(state_path: Path = DEFAULT_STATE_PATH) -> Dict:
    if state_path.exists():
        return json.loads(state_path.read_text(encoding="utf-8"))
    return {"vector_store_id": None, "vector_store_name": None, "chunks": {}}


def save_state(state: Dict, state_path: Path = DEFAULT_STATE_PATH) -> None:
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


# ============================================================
# OpenAI API calls
# ============================================================

def get_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Thiếu OPENAI_API_KEY. Copy .env.sample -> .env và điền key thật."
        )
    return OpenAI(api_key=api_key)


def get_or_create_vector_store(
    client: OpenAI,
    state: Dict,
    name: str = "OptiBot Knowledge Base"
) -> str:
    """
    Tái sử dụng Vector Store cũ (nếu đã lưu trong state) hoặc tạo mới.

    Returns:
        vector_store_id
    """
    if state.get("vector_store_id"):
        try:
            vs = client.vector_stores.retrieve(state["vector_store_id"])
            print(f"[vector_store] Tái sử dụng Vector Store có sẵn: {vs.id} ({vs.name})")
            return vs.id
        except Exception as e:
            print(f"[vector_store] Không tìm lại được store cũ ({e}), tạo mới.")

    vs = client.vector_stores.create(name=name)
    state["vector_store_id"] = vs.id
    state["vector_store_name"] = vs.name
    print(f"[vector_store] Đã tạo Vector Store mới: {vs.id} ({vs.name})")
    return vs.id


def upload_one_chunk(
    client: OpenAI,
    vector_store_id: str,
    chunk: Dict,
    file_path: Path,
    max_retries: int = 3,
) -> Dict:
    """
    Upload 1 chunk (đã ghi ra file_path) lên Vector Store, có retry.

    Returns:
        dict kết quả: {chunk_id, status, openai_file_id | error}
    """
    last_err: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            with open(file_path, "rb") as f:
                vs_file = client.vector_stores.files.upload_and_poll(
                    vector_store_id=vector_store_id,
                    file=f,
                    attributes={
                        "chunk_id": chunk["chunk_id"],
                        "article_id": str(chunk["article_id"]),
                        "article_title": chunk["article_title"][:200],
                        "source_url": chunk["source_url"],
                    },
                    chunking_strategy={
                        "type": "static",
                        "static": {
                            "max_chunk_size_tokens": STATIC_CHUNK_MAX_TOKENS,
                            "chunk_overlap_tokens": STATIC_CHUNK_OVERLAP_TOKENS,
                        },
                    },
                )
            if vs_file.status == "completed":
                return {
                    "chunk_id": chunk["chunk_id"],
                    "status": "completed",
                    "openai_file_id": vs_file.id,
                }
            return {
                "chunk_id": chunk["chunk_id"],
                "status": vs_file.status,
                "openai_file_id": vs_file.id,
                "error": f"status={vs_file.status} (không phải 'completed')",
            }
        except Exception as e:
            last_err = e
            if attempt < max_retries:
                time.sleep(2 ** attempt)  # backoff: 2s, 4s, 8s
    return {
        "chunk_id": chunk["chunk_id"],
        "status": "failed",
        "error": str(last_err),
    }


def upload_chunks(
    client: OpenAI,
    vector_store_id: str,
    chunks: List[Dict],
    file_paths: Dict[str, Path],
    max_workers: int = 8,
) -> List[Dict]:
    """
    Upload nhiều chunk song song (ThreadPoolExecutor - I/O bound, phù hợp threads).

    Returns:
        List kết quả upload (xem upload_one_chunk)
    """
    results = []
    total = len(chunks)
    done = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                upload_one_chunk, client, vector_store_id, c, file_paths[c["chunk_id"]]
            ): c
            for c in chunks
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            done += 1
            if done % 25 == 0 or done == total:
                ok = sum(1 for r in results if r["status"] == "completed")
                print(f"    [{done}/{total}] uploaded (thành công: {ok})")

    return results
