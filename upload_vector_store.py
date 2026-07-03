"""
Phase 2 entry point: upload chunks.jsonl lên OpenAI Vector Store qua API.

Cách chạy:
    python3 upload_vector_store.py                # upload full (lần đầu)
    python3 upload_vector_store.py --dry-run       # build file nội dung, KHÔNG gọi API
    python3 upload_vector_store.py --force         # upload lại toàn bộ, bỏ qua delta-skip
    python3 upload_vector_store.py --limit 20      # chỉ upload 20 chunk đầu (test nhanh)

Sau khi chạy xong, script in ra vector_store_id — dùng ID này để gắn vào
Playground (Prompts/Chat -> Tools -> File search -> chọn/dán Vector Store ID).
"""

import argparse
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.vector_store import (
    DEFAULT_CHUNKS_PATH,
    DEFAULT_STATE_PATH,
    build_file_content,
    content_hash,
    get_client,
    get_or_create_vector_store,
    load_chunks,
    load_state,
    save_state,
    upload_chunks,
    write_chunk_files,
)

TMP_UPLOAD_DIR = Path(".tmp_vector_store_files")


def partition_chunks(chunks, state):
    """
    Chia chunks thành 3 nhóm dựa trên state cũ (đã upload từ lần chạy trước):
        - to_upload: chunk mới HOẶC nội dung đã đổi (content_hash khác)
        - unchanged: chunk đã upload, nội dung y hệt -> bỏ qua (delta upload)

    Đây chính là cơ chế Phase 3 sẽ dùng lại để chỉ upload phần thay đổi mỗi ngày.
    """
    known = state.get("chunks", {})
    to_upload = []
    unchanged = []

    for c in chunks:
        h = content_hash(build_file_content(c))
        prev = known.get(c["chunk_id"])
        if prev and prev.get("content_hash") == h and prev.get("status") == "completed":
            unchanged.append(c)
        else:
            to_upload.append(c)

    return to_upload, unchanged


def main():
    parser = argparse.ArgumentParser(description="Upload chunks lên OpenAI Vector Store")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ build file, không gọi API")
    parser.add_argument("--force", action="store_true", help="Upload lại toàn bộ, bỏ qua delta-skip")
    parser.add_argument("--chunks", default=str(DEFAULT_CHUNKS_PATH), help="Đường dẫn chunks.jsonl")
    parser.add_argument("--max-workers", type=int, default=8, help="Số thread upload song song")
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Giới hạn số chunk upload trong lần chạy này (vd --limit 20 để test nhanh "
             "trước khi upload toàn bộ 1300+ chunk). Không set = upload hết."
    )
    args = parser.parse_args()

    load_dotenv()

    print("=" * 60)
    print("PHASE 2: UPLOAD VECTOR STORE")
    print("=" * 60)

    chunks_path = Path(args.chunks)
    if not chunks_path.exists():
        print(f"Không tìm thấy {chunks_path}. Chạy `python3 main.py` (Phase 1) trước.")
        sys.exit(1)

    print(f"\n[1] Đọc {chunks_path}...")
    chunks = load_chunks(chunks_path)
    print(f"    Tổng: {len(chunks)} chunks")

    state = load_state(DEFAULT_STATE_PATH)

    if args.force:
        to_upload, unchanged = chunks, []
    else:
        to_upload, unchanged = partition_chunks(chunks, state)

    print(f"\n[2] Phân loại delta:")
    print(f"    Cần upload (mới/đổi): {len(to_upload)}")
    print(f"    Bỏ qua (không đổi):   {len(unchanged)}")

    if args.limit is not None:
        held_back = max(0, len(to_upload) - args.limit)
        to_upload = to_upload[:args.limit]
        print(f"    --limit {args.limit} -> chỉ upload {len(to_upload)} chunk "
              f"(giữ lại {held_back} chunk khác cho lần chạy sau)")

    if args.dry_run:
        print("\n[DRY-RUN] Build nội dung file mẫu (không gọi OpenAI API)...")
        TMP_UPLOAD_DIR.mkdir(exist_ok=True)
        sample = to_upload[:3] if to_upload else chunks[:3]
        for c in sample:
            content = build_file_content(c)
            print(f"\n--- {c['chunk_id']} ---")
            print(content[:400])
        print(f"\n[DRY-RUN] Sẽ upload {len(to_upload)} file nếu chạy thật (không có --dry-run).")
        return

    if not to_upload:
        print("\nKhông có gì cần upload. Xong.")
        return

    print(f"\n[3] Ghi {len(to_upload)} chunk thành file tạm ({TMP_UPLOAD_DIR}/)...")
    file_paths = write_chunk_files(to_upload, TMP_UPLOAD_DIR)

    print("\n[4] Kết nối OpenAI, lấy/tạo Vector Store...")
    client = get_client()
    vector_store_id = get_or_create_vector_store(client, state)
    save_state(state, DEFAULT_STATE_PATH)  # lưu ngay vector_store_id, phòng crash giữa chừng

    print(f"\n[5] Upload {len(to_upload)} file lên Vector Store {vector_store_id}...")
    results = upload_chunks(
        client, vector_store_id, to_upload, file_paths, max_workers=args.max_workers
    )

    result_map = {r["chunk_id"]: r for r in results}

    # Cập nhật state với kết quả — LƯU NGAY SAU MỖI CHUNK, không đợi hết batch.
    # Lý do: nếu script bị gián đoạn (mất mạng, Ctrl+C, rate limit...) giữa
    # chừng, những chunk đã upload thành công TRƯỚC đó vẫn phải được ghi vào
    # state ngay lập tức. Nếu chỉ save_state() 1 lần ở cuối, các file đã thật
    # sự tồn tại trên OpenAI nhưng chưa kịp ghi state sẽ bị coi là "chưa
    # upload" ở lần chạy sau -> upload lại -> tạo file trùng trên OpenAI.
    added, updated, failed = 0, 0, 0
    for c in to_upload:
        r = result_map.get(c["chunk_id"])
        if r is None:
            failed += 1
            print(f"    Không tìm thấy kết quả upload cho {c['chunk_id']}")
            continue
        was_new = c["chunk_id"] not in state.get("chunks", {})
        if r["status"] == "completed":
            state.setdefault("chunks", {})[c["chunk_id"]] = {
                "openai_file_id": r["openai_file_id"],
                "article_id": c["article_id"],
                "source_url": c["source_url"],
                "content_hash": content_hash(build_file_content(c)),
                "status": "completed",
            }
            save_state(state, DEFAULT_STATE_PATH)  # lưu ngay, không đợi hết loop
            if was_new:
                added += 1
            else:
                updated += 1
        else:
            failed += 1
            print(f"    LỖI chunk {c['chunk_id']}: {r.get('error')}")

    shutil.rmtree(TMP_UPLOAD_DIR, ignore_errors=True)

    print("\n" + "=" * 60)
    print("KẾT QUẢ")
    print("=" * 60)
    print(f"Added:   {added}")
    print(f"Updated: {updated}")
    print(f"Skipped (không đổi): {len(unchanged)}")
    if args.limit is not None:
        print(f"Giữ lại do --limit:  {held_back}")
    print(f"Failed:  {failed}")
    print(f"\nVector Store ID: {vector_store_id}")
    print("-> Playground: Prompts/Chat > Tools > File search > dán Vector Store ID này")
    print("=" * 60)


if __name__ == "__main__":
    main()