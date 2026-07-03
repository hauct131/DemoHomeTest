"""
Dọn dẹp file trùng lặp trong OpenAI Vector Store.

Nguyên nhân trùng: upload_vector_store.py (bản cũ) chỉ save_state() 1 LẦN ở
cuối batch. Nếu script bị gián đoạn giữa chừng, các file đã upload thành công
lên OpenAI nhưng chưa kịp ghi vào state.json sẽ bị coi là "chưa upload" ở lần
chạy sau -> bị upload lại -> tạo file trùng chunk_id trên OpenAI.

Script này liệt kê toàn bộ file trong Vector Store, gom theo TÊN FILE
(chunk_id.md), với mỗi nhóm trùng: giữ lại bản có created_at MỚI NHẤT
(vì đó là nội dung mới nhất/đúng nhất), xóa các bản cũ hơn.

Cách chạy:
    python3 cleanup_duplicate_files.py                 # dry-run mặc định, chỉ liệt kê
    python3 cleanup_duplicate_files.py --apply          # thực sự xóa file trùng
    python3 cleanup_duplicate_files.py --vector-store-id vs_xxx   # chỉ định store khác state.json

Yêu cầu: đã có OPENAI_API_KEY trong .env hoặc biến môi trường (dùng chung cơ
chế với upload_vector_store.py).
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

DEFAULT_STATE_PATH = Path("vector_store_state.json")


def load_vector_store_id(explicit_id: str | None) -> str:
    if explicit_id:
        return explicit_id
    if not DEFAULT_STATE_PATH.exists():
        raise SystemExit(
            f"Không tìm thấy {DEFAULT_STATE_PATH} và không có --vector-store-id. "
            "Chỉ định 1 trong 2."
        )
    with open(DEFAULT_STATE_PATH, encoding="utf-8") as f:
        state = json.load(f)
    vs_id = state.get("vector_store_id")
    if not vs_id:
        raise SystemExit(f"{DEFAULT_STATE_PATH} không có vector_store_id.")
    return vs_id


def list_all_files(client: OpenAI, vector_store_id: str):
    """Liệt kê toàn bộ file trong vector store, xử lý phân trang."""
    all_files = []
    after = None
    while True:
        page = client.vector_stores.files.list(
            vector_store_id=vector_store_id,
            after=after,
            limit=100,
        )
        all_files.extend(page.data)
        if not page.has_more:
            break
        after = page.data[-1].id
    return all_files


def main():
    parser = argparse.ArgumentParser(description="Dọn file trùng trong OpenAI Vector Store")
    parser.add_argument("--apply", action="store_true",
                         help="Thực sự xóa file trùng. Không truyền = chỉ dry-run liệt kê.")
    parser.add_argument("--vector-store-id", default=None,
                         help="Vector Store ID. Mặc định đọc từ vector_store_state.json")
    args = parser.parse_args()

    load_dotenv()
    client = OpenAI()
    vector_store_id = load_vector_store_id(args.vector_store_id)

    print(f"Vector Store: {vector_store_id}")
    print("Đang liệt kê toàn bộ file (có thể mất chút thời gian nếu nhiều file)...")
    vs_files = list_all_files(client, vector_store_id)
    print(f"Tổng số file trong Vector Store: {len(vs_files)}")

    # Vector store file object không có sẵn 'filename' trực tiếp trong mọi
    # phiên bản SDK -> lấy qua client.files.retrieve(file_id).filename
    print("Đang tra tên file cho từng file_id...")
    by_name = defaultdict(list)
    for i, vf in enumerate(vs_files, 1):
        try:
            file_obj = client.files.retrieve(vf.id)
            filename = file_obj.filename
        except Exception as e:
            filename = f"<lỗi tra tên: {e}>"
        by_name[filename].append({
            "file_id": vf.id,
            "created_at": vf.created_at,
            "status": vf.status,
        })
        if i % 50 == 0:
            print(f"    đã tra {i}/{len(vs_files)}...")

    duplicates = {name: entries for name, entries in by_name.items() if len(entries) > 1}

    print(f"\nSố tên file có bản TRÙNG: {len(duplicates)}")
    total_dup_files = sum(len(v) - 1 for v in duplicates.values())
    print(f"Tổng số file THỪA cần xóa: {total_dup_files}")

    to_delete = []
    for name, entries in duplicates.items():
        entries_sorted = sorted(entries, key=lambda e: e["created_at"], reverse=True)
        keep = entries_sorted[0]
        remove = entries_sorted[1:]
        print(f"\n{name}: {len(entries)} bản")
        print(f"    GIỮ:  {keep['file_id']} (created_at={keep['created_at']})")
        for r in remove:
            print(f"    XÓA:  {r['file_id']} (created_at={r['created_at']})")
            to_delete.append(r["file_id"])

    if not args.apply:
        print(f"\n[DRY-RUN] Sẽ xóa {len(to_delete)} file nếu chạy với --apply.")
        print("Không có gì bị xóa thật.")
        return

    print(f"\nĐang xóa {len(to_delete)} file...")
    deleted, failed = 0, 0
    for file_id in to_delete:
        try:
            # Gỡ khỏi vector store trước, sau đó xóa file khỏi OpenAI storage
            client.vector_stores.files.delete(vector_store_id=vector_store_id, file_id=file_id)
            client.files.delete(file_id)
            deleted += 1
        except Exception as e:
            print(f"    LỖI xóa {file_id}: {e}")
            failed += 1

    print(f"\nHoàn tất. Đã xóa: {deleted}, Lỗi: {failed}")
    print("\nLưu ý: sau khi dọn xong, kiểm tra lại vector_store_state.json để đảm bảo")
    print("chunk_id nào cũng chỉ trỏ tới đúng 1 openai_file_id còn tồn tại (bản GIỮ ở trên).")


if __name__ == "__main__":
    main()