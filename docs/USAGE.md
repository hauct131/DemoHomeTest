# Hướng Dẫn Sử Dụng OptiSigns RAG Pipeline

## Mục Lục

1. [Quick Start](#quick-start)
2. [Cấu trúc Project](#cấu-trúc-project)
3. [Cách Chạy Pipeline](#cách-chạy-pipeline)
4. [Cấu hình](#cấu-hình)
5. [Output Details](#output-details)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)

---

## Quick Start

### 1. Cài đặt Dependencies

```bash
# Install từ requirements.txt
pip3 install --break-system-packages -r requirements.txt

# Hoặc install từng package:
pip3 install --break-system-packages beautifulsoup4 lxml markdownify tiktoken
```

### 2. Chạy Pipeline

```bash
# Cách đơn giản: chạy main.py
python3 main.py

# Output:
#  Xử lý 404 articles
#  Tạo 1,234 chunks
#  Audit report: 50 chunks có issue
```

### 3. Kiểm tra Output

```bash
# Markdown files
ls -la data/output/articles/ | head -10

# Chunks JSONL (mỗi dòng = 1 chunk)
head -1 data/output/chunks.jsonl | python3 -m json.tool

# Audit report
head -5 data/output/audit_report.jsonl
```

---

## Cấu trúc Project

```
DemoHomeTest/
├── data/                        #  Data directory
│   ├── optisigns_articles.json  #  Input (Zendesk dump)
│   ├── vector_store_state.json  #  OpenAI Vector Store sync state
│   └── output/                  #  Output directory
│       ├── articles/            #  Output: Markdown files
│       │   ├── how-to-install-optisigns.md
│       │   ├── troubleshooting-guide.md
│       │   └── ...
│       ├── chunks.jsonl         #  Output: Chunks for embedding
│       └── audit_report.jsonl   #  Output: Quality report
│
├── src/
│   ├── __init__.py              # Package marker
│   ├── config.py                #  ALL constants & config
│   ├── utils.py                 #  Utility functions
│   ├── html_cleaner.py          #  HTML cleaning
│   ├── markdown_converter.py    #  HTML -> Markdown
│   ├── chunking.py              #  Chunking logic
│   ├── audit.py                 #  Quality audit
│   └── pipeline.py              #  Main orchestration
│
├── main.py                      #  Entry point
├── requirements.txt             #  Dependencies
├── README.md                    #  Overview
└── USAGE.md                     #  This file
```

---

## Cách Chạy Pipeline

### Option 1: Command Line (Đơn giản nhất)

```bash
python3 main.py
```

**Output**:
```
============================================================
OptiSigns RAG Pipeline
============================================================

[1] Loading articles from optisigns_articles.json...
    Total: 404 articles

[2] Filtering empty articles (min 200 chars)...
    Skipped: 23
    Remaining: 381

[3] Dedup by title (keeping newest by updated_at)...
    Dedup count: 5
    Final: 376

[4] Building ID->Slug mapping...

[5] Processing 376 articles...
    [1/376] How to Install OptiSigns on Windows...
    [2/376] Understanding Payment Methods...
    ...
    [376/376] Troubleshooting Common Issues...
    Processed: 376
    Total chunks: 1,234

[6] Writing chunks to data/output/chunks.jsonl...
    Done: 1,234 chunks

[7] Running audit...

============================================================
AUDIT CHẤT LƯỢNG CHUNK
============================================================
Tổng chunks: 1,234
Chunks có ít nhất 1 vấn đề: 47 (3.8%)

Bảng thống kê issues:
  too_long                  :   20 ( 1.6%)
  starts_mid_sentence       :   15 ( 1.2%)
  too_short                 :   12 ( 1.0%)

Chi tiết từng chunk lỗi: data/output/audit_report.jsonl
============================================================

 * Output markdown: data/output/articles/ (376 files)
 * Output chunks:   data/output/chunks.jsonl (1,234 lines)
 * Output audit:    data/output/audit_report.jsonl
 * Avg chunks/article: 3.3
============================================================
```

### Option 2: Python Script

```python
from src.pipeline import run_pipeline

# Chạy với default config
stats = run_pipeline(verbose=True)

# Truy cập kết quả
print(f" Processed {stats['processed_articles']} articles")
print(f" Generated {stats['total_chunks']} chunks")
print(f" Avg: {stats['avg_chunks_per_article']:.1f} chunks/article")
print(f" Flagged: {stats['audit_stats']['flagged_chunks']} "
      f"({stats['audit_stats']['flagged_percentage']:.1f}%)")
```

### Option 3: Custom Paths

```python
from pathlib import Path
from src.pipeline import run_pipeline

stats = run_pipeline(
    input_json=Path("my_articles.json"),
    output_docs=Path("my_docs"),
    output_chunks=Path("my_chunks.jsonl"),
    output_audit=Path("my_audit.jsonl"),
    verbose=True
)
```

---

## Cấu hình

### 1. Thay đổi Configuration

Edit `src/config.py`:

```python
# src/config.py

# Ngưỡng lọc articles
MIN_BODY_TEXT_LEN = 300  # Bỏ articles ngắn hơn 300 ký tự

# Chunking settings
MAX_CHUNK_TOKENS = 800   # Max 800 tokens/chunk (default 600)
CHUNK_OVERLAP_TOKENS = 100  # Overlap 100 tokens (default 50)

# Boilerplate patterns
# Thêm pattern để xóa footer nếu cần
BOILERPLATE_HEADING_PATTERNS.append(r"^custom footer\b")
```

### 2. Tùy chỉnh Markdown Conversion

Edit `src/config.py` → `BOILERPLATE_*_REGEXES`:

```python
# Xóa pattern custom (ví dụ: "Powered by XYZ")
BOILERPLATE_PHRASE_REGEXES.append(r"Powered by [a-zA-Z0-9\s]+")
```

### 3. Tùy chỉnh HTML Cleaning

Edit `src/config.py` → `TAGS_TO_STRIP`:

```python
# Xóa thêm tag (ví dụ: <details>)
TAGS_TO_STRIP.append("details")
```

---

## Output Details

### 1. Markdown Files (`data/output/articles/*.md`)

**Format**:
```markdown
---
title: "How to Install on Windows"
source_url: "https://support.optisigns.com/hc/en-us/articles/123456"
article_id: 123456
section_id: 789
created_at: "2024-01-15T10:00:00Z"
updated_at: "2024-03-01T15:30:00Z"
labels: ["installation", "windows", "setup"]
---

# How to Install on Windows

## System Requirements

- Windows 10 or later
- 4GB RAM minimum
- 100MB disk space

## Installation Steps

1. Download the installer from [our website](our-website.md)
2. Run the installer
3. Follow on-screen instructions
...
```

**Sử dụng**:
- Render thành static site
- Import vào CMS
- Sync vào knowledge base

### 2. Chunks JSONL (`data/output/chunks.jsonl`)

**Format** (1 JSON object mỗi dòng):
```json
{
  "chunk_id": "123456-0",
  "article_id": 123456,
  "article_title": "How to Install on Windows",
  "heading": "System Requirements",
  "source_url": "https://support.optisigns.com/hc/en-us/articles/123456",
  "section_id": 789,
  "updated_at": "2024-03-01T15:30:00Z",
  "labels": ["installation", "windows", "setup"],
  "text": "Windows 10 or later\n4GB RAM minimum\n100MB disk space",
  "token_count": 28
}
```

**Sử dụng**:
- Embed vào Vector DB (Pinecone, Weaviate, Milvus)
- RAG (Retrieval Augmented Generation) search
- LLM context retrieval

**Embedding Example**:
```python
import json
from openai import OpenAI

client = OpenAI()

# Đọc chunks
with open("data/output/chunks.jsonl") as f:
    for line in f:
        chunk = json.loads(line)
        
        # Embed text
        embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=chunk["text"]
        )
        
        # Store vào Vector DB với metadata
        vector_db.upsert(
            id=chunk["chunk_id"],
            vector=embedding.data[0].embedding,
            metadata={
                "article_id": chunk["article_id"],
                "article_title": chunk["article_title"],
                "heading": chunk["heading"],
                "source_url": chunk["source_url"],
                "labels": chunk["labels"],
            },
            text=chunk["text"]  # full-text search
        )
```

### 3. Audit Report (`data/output/audit_report.jsonl`)

**Format** (1 JSON object mỗi dòng, chỉ chunks có issue):
```json
{
  "chunk_id": "654321-5",
  "article_title": "Troubleshooting Common Issues",
  "source_url": "https://support.optisigns.com/hc/en-us/articles/654321",
  "issues": ["starts_mid_sentence", "too_short"],
  "text_preview": "and then restart the application..."
}
```

**Issues**:
- `orphan_heading` - Chunk chỉ có heading, không có nội dung
- `starts_mid_sentence` - Bắt đầu bằng chữ thường (khả năng cắt ngang)
- `ends_mid_list` - Kết thúc giữa danh sách
- `broken_code_block` - Code block mở mà không đóng
- `starts_mid_table` - Bắt đầu ở giữa bảng
- `too_short` - < 15 tokens
- `too_long` - > 900 tokens

**Giải quyết**:
```bash
# Xem chunks có issue
cat data/output/audit_report.jsonl | wc -l

# Xem issue statistics
jq -r '.issues[]' data/output/audit_report.jsonl | sort | uniq -c | sort -rn

# Xem preview của từng chunk
jq '.chunk_id, .article_title, .issues, .text_preview' data/output/audit_report.jsonl
```

---

## Troubleshooting

###  Error: File not found: data/optisigns_articles.json

**Nguyên nhân**: Input JSON không ở đúng vị trí

**Giải pháp**:
```bash
# Kiểm tra file tồn tại
ls -la data/optisigns_articles.json

# Nếu chưa có, copy từ nơi khác
cp /path/to/optisigns_articles.json data/

# Hoặc thay đổi path trong config
# src/config.py: INPUT_JSON_PATH = Path("path/to/my_articles.json")
```

###  Error: ModuleNotFoundError: No module named 'markdownify'

**Nguyên nhân**: Dependencies chưa cài

**Giải pháp**:
```bash
pip3 install --break-system-packages -r requirements.txt

# Hoặc install riêng
pip3 install --break-system-packages markdownify beautifulsoup4
```

###  Warning: Fallback token counter (tiktoken not available)

**Nguyên nhân**: tiktoken chưa cài hoặc cài thất bại

**Ảnh hưởng**: Token count sẽ ít chính xác (heuristic ~4 ký tự/token)

**Giải pháp**:
```bash
# Cài tiktoken (nếu cần token count chính xác)
pip3 install --break-system-packages tiktoken

# Nếu cài thất bại, pipeline vẫn chạy bình thường (chỉ fallback)
```

###  Pipeline chạy rất chậm

**Nguyên nhân**: Xử lý lần lượt từng article

**Tối ưu** (Advanced):
```python
# Sử dụng ThreadPool để xử lý parallel
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(process_article, article, ...)
        for article in articles
    ]
    results = [f.result() for f in futures]
```

###  Output files quá lớn

**Nguyên nhân**: Quá nhiều chunks hoặc tokens dài

**Giải pháp**:
```python
# Trong src/config.py, giảm max tokens
MAX_CHUNK_TOKENS = 400  # Từ 600 xuống 400

# Hoặc bỏ articles không cần thiết (MIN_BODY_TEXT_LEN cao hơn)
MIN_BODY_TEXT_LEN = 500  # Từ 200 lên 500
```

---

## Advanced Usage

### 1. Custom Boilerplate Patterns

```python
# src/config.py

# Thêm pattern detect phần "Share" ở cuối articles
BOILERPLATE_PHRASE_REGEXES.append(
    r"^#+\s*Share\s*(?:this\s*)?(?:article|page)?"
)
```

### 2. Custom Chunking Strategy

```python
# src/chunking.py

def chunk_markdown_custom(markdown_text, title):
    """Custom chunking bằng fixed-size chunks (thay vì heading-based)."""
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for paragraph in markdown_text.split("\n\n"):
        para_tokens = count_tokens(paragraph)
        
        if current_tokens + para_tokens > MAX_CHUNK_TOKENS:
            chunks.append({"heading": title, "text": "\n\n".join(current_chunk)})
            current_chunk = [paragraph]
            current_tokens = para_tokens
        else:
            current_chunk.append(paragraph)
            current_tokens += para_tokens
    
    if current_chunk:
        chunks.append({"heading": title, "text": "\n\n".join(current_chunk)})
    
    return chunks
```

### 3. Custom Metadata

```python
# src/pipeline.py

def enrich_chunk_with_custom_metadata(chunk, article):
    """Thêm metadata custom (ví dụ: priority, category)."""
    chunk["priority"] = "high" if article.get("views", 0) > 1000 else "low"
    chunk["category"] = article.get("category", "general")
    return chunk
```

### 4. Export sang định dạng khác

```python
# Export sang CSV
import csv

with open("data/output/chunks.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["chunk_id", "article_id", "heading", "text"])
    writer.writeheader()
    
    with open("data/output/chunks.jsonl") as jf:
        for line in jf:
            chunk = json.loads(line)
            writer.writerow({
                "chunk_id": chunk["chunk_id"],
                "article_id": chunk["article_id"],
                "heading": chunk["heading"],
                "text": chunk["text"][:100] + "..."  # truncate
            })
```

### 5. Integration với RAG Framework

```python
# Ví dụ: Langchain + LLamaIndex

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.embeddings import OpenAIEmbedding

# Load markdown documents
documents = SimpleDirectoryReader("data/output/articles").load_data()

# Create index
embed_model = OpenAIEmbedding(model="text-embedding-3-small")
index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

# Query
query_engine = index.as_query_engine()
response = query_engine.query("How to install OptiSigns on Windows?")
print(response)
```

---

## Performance Optimization

### 1. Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_articles_parallel(articles, max_workers=4):
    chunks = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_article, a, ...): a
            for a in articles
        }
        
        for future in as_completed(futures):
            _, chunks_list = future.result()
            chunks.extend(chunks_list)
    
    return chunks
```

### 2. Batch Writing

```python
# Write chunks mỗi 100 chunks thay vì mỗi chunk
BATCH_SIZE = 100
buffer = []

for chunk in all_chunks:
    buffer.append(chunk)
    
    if len(buffer) >= BATCH_SIZE:
        with open("data/output/chunks.jsonl", "a") as f:
            for c in buffer:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
        buffer = []
```

### 3. Memory-Efficient Processing

```python
# Process articles từng batch thay vì load hết vào memory
def process_articles_streaming(json_path, batch_size=50):
    with open(json_path) as f:
        articles = json.load(f)
    
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i+batch_size]
        yield from process_batch(batch)
```

---

## Next Steps

1. **Integrate với Vector DB**: Embed chunks vào Pinecone/Weaviate
2. **Build RAG Application**: Sử dụng chunks cho LLM context retrieval
3. **Monitor Quality**: Track audit scores theo thời gian
4. **Automate Updates**: Chạy pipeline định kỳ khi có articles mới
5. **Scale**: Implement parallel processing cho 1000s articles

---

**Version**: 1.0  
**Last Updated**: 2024-07-03  
**Maintained by**: OptiSigns Team
