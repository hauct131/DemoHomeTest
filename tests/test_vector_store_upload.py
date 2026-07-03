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


def test_build_file_content_has_article_url_line():
    c = make_fake_chunk()
    content = build_file_content(c)
    assert content.startswith("Article URL: https://x.com/a"), content
    assert "Test Article — Test Heading" in content
    print("OK: build_file_content có dòng Article URL đúng format")


def test_upload_one_chunk_success():
    fake_client = MagicMock()
    fake_client.vector_stores.files.upload_and_poll.return_value = SimpleNamespace(
        id="file_123", status="completed"
    )
    c = make_fake_chunk()
    with tempfile.TemporaryDirectory() as tmp:
        paths = write_chunk_files([c], Path(tmp))
        result = upload_one_chunk(fake_client, "vs_1", c, paths[c["chunk_id"]])
    assert result["status"] == "completed"
    assert result["openai_file_id"] == "file_123"
    print("OK: upload_one_chunk trả về đúng khi API thành công")


def test_upload_one_chunk_retries_then_fails():
    fake_client = MagicMock()
    fake_client.vector_stores.files.upload_and_poll.side_effect = Exception("network error")
    c = make_fake_chunk()
    with tempfile.TemporaryDirectory() as tmp:
        paths = write_chunk_files([c], Path(tmp))
        result = upload_one_chunk(
            fake_client, "vs_1", c, paths[c["chunk_id"]], max_retries=2
        )
    assert result["status"] == "failed"
    assert fake_client.vector_stores.files.upload_and_poll.call_count == 2
    print("OK: upload_one_chunk retry đúng số lần rồi mới fail")


def test_upload_chunks_concurrent():
    fake_client = MagicMock()
    fake_client.vector_stores.files.upload_and_poll.return_value = SimpleNamespace(
        id="file_x", status="completed"
    )
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
    test_upload_chunks_concurrent()
    test_content_hash_detects_change()
    print("\nTất cả test PASS.")
