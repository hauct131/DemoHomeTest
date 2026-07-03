"""
TẦNG 1: Kiểm tra TÍNH ĐÚNG ĐẮN của dữ liệu đã upload lên OpenAI Vector Store.

Đối chiếu 3 nguồn:
    (A) chunks.jsonl        - dữ liệu gốc, "sự thật" cần có
    (B) vector_store_state.json - local state script tự ghi lại
    (C) OpenAI Vector Store thật - list file trực tiếp qua API

Phát hiện:
    - Chunk có trong (A) nhưng KHÔNG có trong (B) -> chưa upload
    - Chunk có trong (B) nhưng KHÔNG còn trong (C) -> bị xóa nhầm / state cũ
    - File trong (C) không map được về chunk_id nào trong (B) -> file rác/mồ côi
    - Trùng tên file (chunk_id.md) trong (C) -> chưa dọn hết (chạy cleanup_duplicate_files.py)
    - content_hash giữa (A) và (B) lệch nhau -> nội dung đã đổi nhưng CHƯA re-upload
    - status != "completed" trên OpenAI -> file lỗi xử lý, cần upload lại

Cách chạy:
    python3 verify_vector_store.py
"""

import sys
from pathlib import Path

# Thêm project root vào sys.path để import src/
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src import config

import json
from collections import Counter, defaultdict

from dotenv import load_dotenv
from openai import OpenAI

CHUNKS_PATH = config.OUTPUT_CHUNKS_PATH
STATE_PATH = config.VECTOR_STORE_STATE_PATH


def content_hash_of(chunk: dict) -> str:
    """Copy logic hash y hệt src/vector_store.py để so sánh đúng chuẩn."""
    import hashlib
    text = f"Article URL: {chunk['source_url']}\n\n{chunk['embedding_text']}"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_chunks_jsonl(path: Path) -> dict:
    chunks = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                c = json.loads(line)
                chunks[c["chunk_id"]] = c
    return chunks


def list_all_vs_files(client: OpenAI, vector_store_id: str):
    all_files = []
    after = None
    while True:
        page = client.vector_stores.files.list(vector_store_id=vector_store_id, after=after, limit=100)
        all_files.extend(page.data)
        if not page.has_more:
            break
        after = page.data[-1].id
    return all_files


def main():
    load_dotenv()

    if not CHUNKS_PATH.exists():
        raise SystemExit(f"Không tìm thấy {CHUNKS_PATH}")
    if not STATE_PATH.exists():
        raise SystemExit(f"Không tìm thấy {STATE_PATH}")

    local_chunks = load_chunks_jsonl(CHUNKS_PATH)
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state_chunks = state.get("chunks", {})
    vector_store_id = state.get("vector_store_id")

    if not vector_store_id:
        raise SystemExit("state.json không có vector_store_id.")

    print(f"(A) chunks.jsonl:        {len(local_chunks)} chunk")
    print(f"(B) vector_store_state:  {len(state_chunks)} chunk")

    client = OpenAI()
    print(f"(C) Đang lấy danh sách file thật từ OpenAI Vector Store {vector_store_id}...")
    vs_files = list_all_vs_files(client, vector_store_id)
    print(f"(C) OpenAI Vector Store: {len(vs_files)} file thật\n")

    # ---- 1. Chunk chưa upload (có trong A, không có trong B) ----
    missing_upload = [cid for cid in local_chunks if cid not in state_chunks]
    print(f"[1] Chunk CHƯA upload (có trong chunks.jsonl, chưa có trong state): {len(missing_upload)}")
    for cid in missing_upload[:10]:
        print(f"      - {cid}")
    if len(missing_upload) > 10:
        print(f"      ... và {len(missing_upload)-10} chunk khác")

    # ---- 2. content_hash lệch (nội dung đổi nhưng chưa re-upload) ----
    stale = []
    for cid, c in local_chunks.items():
        rec = state_chunks.get(cid)
        if rec and rec.get("content_hash") != content_hash_of(c):
            stale.append(cid)
    print(f"\n[2] Chunk ĐÃ ĐỔI nội dung nhưng chưa re-upload (content_hash lệch): {len(stale)}")
    for cid in stale[:10]:
        print(f"      - {cid}")

    # ---- 3. So khớp state với OpenAI thật ----
    vs_file_ids = {f.id for f in vs_files}
    orphan_in_state = [cid for cid, r in state_chunks.items() if r.get("openai_file_id") not in vs_file_ids]
    print(f"\n[3] Chunk trong state trỏ tới file_id KHÔNG CÒN tồn tại trên OpenAI: {len(orphan_in_state)}")
    for cid in orphan_in_state[:10]:
        print(f"      - {cid} -> {state_chunks[cid].get('openai_file_id')}")

    # ---- 4. File trên OpenAI không map được về chunk nào trong state (rác/mồ côi) ----
    known_file_ids = {r.get("openai_file_id") for r in state_chunks.values()}
    orphan_on_openai = [f for f in vs_files if f.id not in known_file_ids]
    print(f"\n[4] File tồn tại trên OpenAI nhưng KHÔNG được track trong state (rác/mồ côi): {len(orphan_on_openai)}")
    for f in orphan_on_openai[:10]:
        print(f"      - {f.id} (status={f.status}, created_at={f.created_at})")

    # ---- 5. Trùng tên file trên OpenAI (chưa dọn hết) ----
    print(f"\n[5] Kiểm tra trùng tên file trên OpenAI (đang tra tên, có thể mất chút thời gian)...")
    by_name = defaultdict(list)
    for f in vs_files:
        try:
            fname = client.files.retrieve(f.id).filename
        except Exception:
            fname = "<lỗi tra tên>"
        by_name[fname].append(f.id)
    dup_names = {n: ids for n, ids in by_name.items() if len(ids) > 1}
    print(f"    Số tên file bị trùng: {len(dup_names)}")
    if dup_names:
        print("    -> Chạy cleanup_duplicate_files.py để dọn.")
        for n, ids in list(dup_names.items())[:5]:
            print(f"      - {n}: {ids}")

    # ---- 6. File status != completed ----
    not_completed = [f for f in vs_files if f.status != "completed"]
    print(f"\n[6] File có status khác 'completed' trên OpenAI: {len(not_completed)}")
    for f in not_completed[:10]:
        print(f"      - {f.id}: status={f.status}")

    # ---- Tổng kết ----
    total_issues = (
        len(missing_upload) + len(stale) + len(orphan_in_state)
        + len(orphan_on_openai) + len(dup_names) + len(not_completed)
    )
    print("\n" + "=" * 60)
    if total_issues == 0:
        print("KẾT QUẢ: Dữ liệu khớp hoàn toàn giữa local và OpenAI. Sạch.")
    else:
        print(f"KẾT QUẢ: Phát hiện {total_issues} vấn đề (xem chi tiết ở trên).")
    print("=" * 60)


if __name__ == "__main__":
    main()