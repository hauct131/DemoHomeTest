# OptiSigns RAG Pipeline - Professional Python Project

Một pipeline xử lý chuyên nghiệp để chuyển đổi Zendesk Help Center dump (JSON) thành:
- Markdown files với front-matter (`output/articles/`)
- Chunks dạng JSONL cho Vector DB embedding (`output/chunks.jsonl`)
- Audit report kiểm tra chất lượng (`output/audit_report.jsonl`)

## Cấu trúc Project

```
DemoHomeTest/
├── data/                       # Thư mục chứa dữ liệu đầu vào
│   └── optisigns_articles.json # File input Zendesk dump
├── docs/                       # Tài liệu hướng dẫn & giải thích dự án
│   ├── 00_START_HERE.md
│   ├── DEVELOPMENT.md
│   ├── FIRST_RUN.md
│   ├── QUICK_REF.md
│   ├── REFACTOR_SUMMARY.md
│   └── USAGE.md
├── output/                     # Thư mục đầu ra tự động tạo
│   ├── articles/               # Chứa các file Markdown đầu ra
│   ├── chunks.jsonl            # Chunks cho embedding
│   ├── audit_report.jsonl      # Báo cáo audit chất lượng chunk
│   └── vector_store_state.json # Trạng thái đồng bộ OpenAI vector store
├── scripts/                    # Scripts bổ trợ chạy độc lập
│   ├── crawl.py
│   ├── upload_vector_store.py
│   ├── verify_vector_store.py
│   └── cleanup_duplicate_files.py
├── src/                        # Source code các modules chính của pipeline
│   ├── __init__.py
│   ├── config.py               # Constants & config tập trung
│   ├── utils.py                # Hàm tiện ích (slugify, token count, v.v.)
│   ├── html_cleaner.py         # Làm sạch HTML
│   ├── markdown_converter.py   # HTML -> Markdown, normalize, boilerplate removal
│   ├── chunking.py             # Logic chia chunks
│   ├── audit.py                # Kiểm tra chất lượng chunk
│   ├── pipeline.py             # Điều phối pipeline chính
│   └── vector_store.py         # Logic kết nối & upload OpenAI vector store
├── tests/                      # Unit tests
│   └── test_vector_store_upload.py
├── main.py                     # Entry point chính chạy pipeline
├── requirements.txt            # Python dependencies
└── .gitignore
```

## Installation

### 1. Clone/Prepare Project

```bash
cd /path/to/Home_Test_CTH
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Hoặc install từng package:

```bash
pip install beautifulsoup4 lxml markdownify tiktoken
```

**Note**: `tiktoken` dùng để đếm token chính xác (OpenAI's cl100k_base encoding). 
Nếu cài đặt không thành công, pipeline sẽ fallback về heuristic (~4 ký tự/token).

## Cách Chạy

### Chạy toàn bộ pipeline:

```bash
python main.py
```

### Chạy trong Python script:

```python
from src.pipeline import run_pipeline

stats = run_pipeline(verbose=True)
print(f"Processed {stats['processed_articles']} articles")
print(f"Generated {stats['total_chunks']} chunks")
```

## Output

### 1. `output/articles/` directory

Markdown files với YAML front-matter:

```markdown
---
title: "How to Install OptiSigns"
source_url: "https://support.optisigns.com/hc/en-us/articles/..."
article_id: 123456
section_id: 789
created_at: "2024-01-15T10:00:00Z"
updated_at: "2024-03-01T15:30:00Z"
labels: ["installation", "setup"]
---

# How to Install OptiSigns

[Content here...]
```

### 2. `output/chunks.jsonl`

Một JSON object mỗi dòng (newline-delimited JSON):

```json
{
  "chunk_id": "123456-0",
  "article_id": 123456,
  "article_title": "How to Install OptiSigns",
  "heading": "Installation Steps",
  "source_url": "https://support.optisigns.com/hc/en-us/articles/...",
  "section_id": 789,
  "updated_at": "2024-03-01T15:30:00Z",
  "labels": ["installation", "setup"],
  "text": "Step 1: Download the installer from our website...",
  "token_count": 125
}
```

Dùng để embed vào Vector DB (Pinecone, Weaviate, v.v.)

### 3. `output/audit_report.jsonl`

Báo cáo từng chunk có vấn đề gì:

```json
{
  "chunk_id": "123456-5",
  "article_title": "How to Install OptiSigns",
  "source_url": "https://support.optisigns.com/hc/en-us/articles/...",
  "issues": ["starts_mid_sentence", "too_short"],
  "text_preview": "... and then click Install button"
}
```

**Issues** có thể bao gồm:
- `orphan_heading`: Chunk chỉ có heading, không có nội dung
- `starts_mid_sentence`: Chunk bắt đầu giữa câu (khả năng bị cắt ngang)
- `ends_mid_list`: Chunk kết thúc giữa danh sách
- `broken_code_block`: Code block bị mở mà không đóng
- `starts_mid_table`: Chunk bắt đầu ở giữa bảng
- `too_short`: Quá ngắn (< 15 tokens)
- `too_long`: Quá dài (> 900 tokens)

## Cấu hình

Tất cả config được lưu trong `src/config.py`:

```python
# Đường dẫn file
INPUT_JSON_PATH = PROJECT_ROOT / "data" / "optisigns_articles.json"
OUTPUT_DOCS_PATH = PROJECT_ROOT / "output" / "articles"
OUTPUT_CHUNKS_PATH = PROJECT_ROOT / "output" / "chunks.jsonl"
OUTPUT_AUDIT_PATH = PROJECT_ROOT / "output" / "audit_report.jsonl"

# Ngưỡng
MIN_BODY_TEXT_LEN = 200  # Bỏ article ngắn hơn
MAX_CHUNK_TOKENS = 600   # Token tối đa mỗi chunk
CHUNK_OVERLAP_TOKENS = 50

# Boilerplate patterns
BOILERPLATE_HEADING_PATTERNS = [...]  # Footer headings
BOILERPLATE_AD_PARAGRAPH_REGEXES = [...]  # Ad paragraphs
```

Để thay đổi, edit `src/config.py` trước khi chạy pipeline.

## Features

###  Làm sạch HTML

-  Xóa `<script>`, `<style>`, `<iframe>`, v.v.
-  Xóa Table of Contents (TOC) nội bộ
-  Xóa anchor targets rỗng
-  Replace images bằng `[Image: filename]`
-  Rewrite internal links sang slug tương ứng

###  Chuẩn hóa Markdown

-  Xóa boilerplate footer sections ("Need Help", "Contact Us", v.v.)
-  Xóa inline boilerplate (OptiSigns ads, emails)
-  Xóa base64 images
-  Rút gọn URLs dài (giảm token)
-  Chuẩn hóa whitespace

###  Chunking thông minh

-  Chia theo heading cấp 2 (##)
-  Tách text dài theo paragraph, giữ overlap
-  Bảo toàn code blocks (không tách ngang)
-  Lọc heading rỗng, junk chunks
-  Hàn nối chunks bị cắt giữa câu

###  Audit chất lượng

-  Phát hiện orphan headings
-  Phát hiện chunks bị cắt giữa câu
-  Phát hiện code blocks bị mở
-  Phát hiện tables bị cắt
-  Báo cáo tất cả issues

###  Code Quality

-  Type hints đầy đủ
-  Docstrings chi tiết
-  PEP 8 compliant
-  Exception handling
-  Modular design

## Troubleshooting

### Error: Input file not found

```
FileNotFoundError: Input file not found: optisigns_articles.json
```

**Giải pháp**: Đảm bảo file `optisigns_articles.json` nằm ở thư mục `data/` của project.

### Error: No module named 'tiktoken'

```
ModuleNotFoundError: No module named 'tiktoken'
```

**Giải pháp**: Cài đặt tiktoken:
```bash
pip install tiktoken
```

Nếu cài đặt thất bại, pipeline sẽ fallback về heuristic (không lỗi, chỉ token count kém chính xác).

### Warning: Some chunks flagged in audit

Nếu `output/audit_report.jsonl` có nhiều chunk có issue, hãy:

1. Xem chi tiết từng issue: `cat output/audit_report.jsonl | head -10`
2. Điều chỉnh config (ví dụ tăng `MAX_CHUNK_TOKENS`)
3. Chạy lại pipeline

### Output files không được tạo

Kiểm tra:
- [ ] Directory `output/articles/` có quyền write
- [ ] Không có file `output/chunks.jsonl` / `output/audit_report.jsonl` bị lock
- [ ] Input JSON có valid format

## Development

### Thêm feature mới

1. **Tạo hàm mới** trong module phù hợp (ví dụ: `src/utils.py`)
2. **Viết docstring** đầy đủ
3. **Thêm type hints**
4. **Import** vào `pipeline.py` nếu cần
5. **Test** trước khi commit

### Ví dụ: Thêm hàm mới

```python
# src/utils.py

def custom_filter(text: str, pattern: str) -> str:
    """
    Filter text theo pattern regex.
    
    Args:
        text: Input text
        pattern: Regex pattern
        
    Returns:
        Filtered text
    """
    return re.sub(pattern, "", text)
```

Rồi dùng trong pipeline:

```python
# src/pipeline.py

from .utils import custom_filter

# ...
cleaned = custom_filter(text, r"some_pattern")
```

## Performance

Để xử lý toàn bộ 400+ articles:

- **Time**: ~5-10 phút (tùy vào máy)
- **Memory**: ~500MB-1GB
- **Disk**: ~50-100MB (output files)

Có thể optimize bằng:
- Xử lý parallel (Thread/Process Pool)
- Batch processing
- Caching boilerplate patterns

## License

Internal project - OptiSigns

## Contact

Để hỏi, report issues, hoặc suggest features: [your contact info]
# DemoHomeTest
