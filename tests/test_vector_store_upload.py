"""
Test upload logic bằng mock OpenAI client (không gọi API thật).
Chạy: python3 -m tests.test_vector_store_upload
"""

import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.vector_store import (
    build_file_content,
    content_hash,
    upload_chunks,
    upload_one_chunk,
    write_chunk_files,
)


def make_fake_chunk(chunk_id="a-0", url="https://x.com/a"):
    return {
        "chunk_id": chunk_id,
        "article_id": 111,
        "article_title": "Test Article",
        "heading": "Test Heading",
        "source_url": url,
        "text": "Nội dung test.",
        "embedding_text": "Test Article — Test Heading\n\nNội dung test.",
        "token_count": 10,
        "embedding_token_count": 15,
    }


def make_fake_client(create_file_id="file_123", final_status="completed"):
    """Tạo mock client mô phỏng đúng 3 lệnh API mà upload_one_chunk gọi:
    files.create -> vector_stores.files.create -> vector_stores.files.retrieve"""
    client = MagicMock()
    client.files.create.return_value = SimpleNamespace(id=create_file_id)
    client.vector_stores.files.create.return_value = SimpleNamespace(
        id=create_file_id, status=final_status
    )
    client.vector_stores.files.retrieve.return_value = SimpleNamespace(
        id=create_file_id, status=final_status
    )
    return client


def test_build_file_content_has_article_url_line():
    c = make_fake_chunk()
    content = build_file_content(c)
    assert content.startswith("Article URL: https://x.com/a"), content
    assert "Test Article — Test Heading" in content
    print("OK: build_file_content có dòng Article URL đúng format")


def test_upload_one_chunk_success():
    fake_client = make_fake_client()
    c = make_fake_chunk()
    with tempfile.TemporaryDirectory() as tmp:
        paths = write_chunk_files([c], Path(tmp))
        result = upload_one_chunk(fake_client, "vs_1", c, paths[c["chunk_id"]])
    assert result["status"] == "completed"
    assert result["openai_file_id"] == "file_123"
    assert fake_client.files.create.call_count == 1
    print("OK: upload_one_chunk trả về đúng khi API thành công")


def test_upload_one_chunk_retries_then_fails():
    fake_client = MagicMock()
    fake_client.files.create.side_effect = Exception("network error")
    c = make_fake_chunk()
    with tempfile.TemporaryDirectory() as tmp:
        paths = write_chunk_files([c], Path(tmp))
        result = upload_one_chunk(
            fake_client, "vs_1", c, paths[c["chunk_id"]], max_retries=2
        )
    assert result["status"] == "failed"
    assert fake_client.files.create.call_count == 2
    print("OK: upload_one_chunk retry đúng số lần rồi mới fail")


def test_upload_one_chunk_retry_does_not_duplicate_file():
    """
    Test QUAN TRỌNG cho bug đã sửa: nếu bước upload (files.create) THÀNH CÔNG
    nhưng bước attach vào vector store (vector_stores.files.create) lỗi mạng ở
    lần thử đầu, lần retry KHÔNG được gọi files.create lần thứ 2 (tức không
    tạo file mới) - phải tái sử dụng đúng file_id đã có.
    """
    fake_client = MagicMock()
    fake_client.files.create.return_value = SimpleNamespace(id="file_only_once")

    # Lần gọi đầu của vector_stores.files.create ném lỗi mạng (giả lập),
    # lần gọi thứ 2 (ở retry) mới thành công.
    fake_client.vector_stores.files.create.side_effect = [
        Exception("transient network error while attaching"),
        SimpleNamespace(id="file_only_once", status="completed"),
    ]

    c = make_fake_chunk()
    with tempfile.TemporaryDirectory() as tmp:
        paths = write_chunk_files([c], Path(tmp))
        result = upload_one_chunk(
            fake_client, "vs_1", c, paths[c["chunk_id"]], max_retries=3
        )

    assert result["status"] == "completed"
    assert result["openai_file_id"] == "file_only_once"
    # Đây là assertion cốt lõi: files.create (upload bytes) CHỈ được gọi 1 LẦN
    # dù toàn bộ quá trình phải retry, vì file_id được nhớ lại giữa các lần thử.
    assert fake_client.files.create.call_count == 1, (
        f"files.create bị gọi {fake_client.files.create.call_count} lần "
        "-> đang tạo file trùng khi retry!"
    )
    print("OK: retry ở bước attach/poll KHÔNG tạo file trùng (bug đã được sửa)")


def test_upload_one_chunk_resumes_polling_on_retry():
    """Nếu attach thành công nhưng poll lỗi mạng thoáng qua, retry phải RESUME
    poll trên cùng file_id, không upload lại từ đầu."""
    fake_client = MagicMock()
    fake_client.files.create.return_value = SimpleNamespace(id="file_resume")
    fake_client.vector_stores.files.create.return_value = SimpleNamespace(
        id="file_resume", status="in_progress"
    )
    # retrieve: lần đầu ném lỗi mạng, lần sau trả về completed
    fake_client.vector_stores.files.retrieve.side_effect = [
        Exception("transient network error while polling"),
        SimpleNamespace(id="file_resume", status="completed"),
    ]

    c = make_fake_chunk()
    with tempfile.TemporaryDirectory() as tmp:
        paths = write_chunk_files([c], Path(tmp))
        result = upload_one_chunk(
            fake_client, "vs_1", c, paths[c["chunk_id"]], max_retries=3
        )

    assert result["status"] == "completed"
    assert fake_client.files.create.call_count == 1
    assert fake_client.vector_stores.files.create.call_count == 1
    print("OK: retry ở bước poll cũng không tạo file trùng, chỉ resume poll")


def test_upload_chunks_concurrent():
    fake_client = make_fake_client(create_file_id="file_x")
    chunks = [make_fake_chunk(chunk_id=f"a-{i}") for i in range(5)]
    with tempfile.TemporaryDirectory() as tmp:
        paths = write_chunk_files(chunks, Path(tmp))
        results = upload_chunks(fake_client, "vs_1", chunks, paths, max_workers=3)
    assert len(results) == 5
    assert all(r["status"] == "completed" for r in results)
    print("OK: upload_chunks xử lý đúng khi chạy song song")


def test_content_hash_detects_change():
    c1 = build_file_content(make_fake_chunk())
    c2 = build_file_content(make_fake_chunk())
    c3 = build_file_content({
        **make_fake_chunk(),
        "embedding_text": "Test Article — Test Heading\n\nNội dung ĐÃ đổi.",
    })
    assert content_hash(c1) == content_hash(c2)
    assert content_hash(c1) != content_hash(c3)
    print("OK: content_hash phát hiện đúng khi nội dung thay đổi (dùng cho Phase 3 delta)")


if __name__ == "__main__":
    test_build_file_content_has_article_url_line()
    test_upload_one_chunk_success()
    test_upload_one_chunk_retries_then_fails()
    test_upload_one_chunk_retry_does_not_duplicate_file()
    test_upload_one_chunk_resumes_polling_on_retry()
    test_upload_chunks_concurrent()
    test_content_hash_detects_change()
    print("\nTất cả test PASS.")