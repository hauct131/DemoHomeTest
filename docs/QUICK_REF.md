# Quick Reference - OptiSigns RAG Pipeline

##  Quick Start

```bash
# 1. Cài dependencies
pip3 install --break-system-packages -r requirements.txt

# 2. Chạy pipeline
python3 main.py

# 3. Kiểm tra output
ls -la docs/
head chunks.jsonl | python3 -m json.tool
wc -l audit_report.jsonl
```

---

##  File Structure

```
src/
├── config.py          ←  TẤT CẢ config, constants
├── utils.py           ←  Utility functions
├── html_cleaning.py   ←  HTML cleaning
├── markdown_conversion.py  ←  Markdown
├── chunking.py        ←  Chunking logic
├── audit.py           ←  Audit/QC
└── pipeline.py        ←  Main orchestration

main.py               ←  Entry point
requirements.txt      ←  Dependencies
```

---

##  Common Tasks

### Thay đổi Config

```python
# src/config.py
MIN_BODY_TEXT_LEN = 300        # Lọc articles dài hơn
MAX_CHUNK_TOKENS = 800         # Max tokens/chunk
CHUNK_OVERLAP_TOKENS = 100     # Overlap size

# Thêm boilerplate pattern
BOILERPLATE_HEADING_PATTERNS.append(r"^footer\b")
```

### Thêm Boilerplate Pattern

```python
# src/config.py - ngay dưới dòng khác

BOILERPLATE_PHRASE_REGEXES.append(
    r"pattern to remove"
)
```

### Debug: Xem chi tiết 1 chunk

```bash
# Xem first chunk
head -1 chunks.jsonl | python3 -m json.tool

# Xem chunks có issue
cat audit_report.jsonl | head -5 | python3 -m json.tool
```

### Export sang CSV

```python
import json
import csv

with open("chunks.jsonl") as jf, open("chunks.csv", "w") as cf:
    reader = json.load(jf)
    writer = csv.DictWriter(cf, fieldnames=["chunk_id", "article_title", "text"])
    writer.writeheader()
    
    for line in jf:
        chunk = json.loads(line)
        writer.writerow({
            "chunk_id": chunk["chunk_id"],
            "article_title": chunk["article_title"],
            "text": chunk["text"][:100]
        })
```

### Chạy cụ thể bước nào đó

```python
# Custom pipeline: chỉ xử lý, bỏ qua audit
from src.pipeline import load_articles, filter_empty_articles
from src.pipeline import dedup_articles_by_title
from src.chunking import chunk_markdown

articles = load_articles("optisigns_articles.json")
filtered, _ = filter_empty_articles(articles, 200)
dedup, _ = dedup_articles_by_title(filtered)

# Xử lý từng article
for article in dedup[:5]:  # Chỉ 5 bài đầu
    from src.html_cleaning import clean_html
    from src.markdown_conversion import html_to_markdown, normalize_markdown
    
    html = article["body"]
    cleaned = clean_html(html)
    md = html_to_markdown(cleaned)
    md = normalize_markdown(md)
    chunks = chunk_markdown(md, article["title"])
    
    print(f"{article['title']}: {len(chunks)} chunks")
```

---

##  Troubleshooting

| Vấn đề | Giải pháp |
|--------|----------|
| `ModuleNotFoundError: markdownify` | `pip3 install --break-system-packages -r requirements.txt` |
| `FileNotFoundError: optisigns_articles.json` | Đảm bảo file ở thư mục gốc cùng `main.py` |
| Pipeline chạy chậm | Giảm `MAX_CHUNK_TOKENS` trong `config.py` |
| Output quá lớn | Tăng `MIN_BODY_TEXT_LEN` để bỏ articles ngắn |
| Nhiều chunks có issue | Xem `audit_report.jsonl`, adjust config |

---

##  Output Format

### chunks.jsonl (mỗi dòng = 1 JSON object)

```json
{
  "chunk_id": "123456-0",
  "article_id": 123456,
  "article_title": "How to Install",
  "heading": "Installation Steps",
  "source_url": "https://support.optisigns.com/hc/en-us/articles/123456",
  "section_id": 789,
  "updated_at": "2024-03-01T15:30:00Z",
  "labels": ["installation", "setup"],
  "text": "Step 1...",
  "token_count": 125
}
```

### docs/*.md (Markdown with Front-Matter)

```markdown
---
title: "How to Install"
source_url: "https://..."
article_id: 123456
section_id: 789
created_at: "2024-01-15T10:00:00Z"
updated_at: "2024-03-01T15:30:00Z"
labels: ["installation", "setup"]
---

# How to Install

Content here...
```

### audit_report.jsonl (chỉ chunks có issue)

```json
{
  "chunk_id": "654321-5",
  "article_title": "Troubleshooting",
  "source_url": "https://...",
  "issues": ["starts_mid_sentence", "too_short"],
  "text_preview": "and then restart..."
}
```

---

##  Performance Stats

| Metric | Typical Value |
|--------|--------------|
| Total Articles | 404 |
| Filtered (empty) | 23 |
| Dedup (duplicates) | 5 |
| Final Articles | 376 |
| Total Chunks | 1,234 |
| Avg Chunks/Article | 3.3 |
| Flagged Chunks (%) | 3.8% |
| Processing Time | 5-10 min |
| Memory Usage | 500MB-1GB |

---

##  Key Functions

| Function | Module | Purpose |
|----------|--------|---------|
| `run_pipeline()` | pipeline | Main orchestration |
| `chunk_markdown()` | chunking | Create chunks |
| `normalize_markdown()` | markdown_conversion | Clean markdown |
| `clean_html()` | html_cleaning | Clean HTML |
| `audit_chunk()` | audit | Check quality |
| `slugify()` | utils | Create file slugs |
| `count_tokens()` | utils | Count tokens |

---

##  Documentation Files

- **README.md** - Project overview
- **USAGE.md** - Detailed usage guide
- **DEVELOPMENT.md** - Developer guide
- **requirements.txt** - Dependencies
- **main.py** - Entry point
- **src/config.py** - All config

---

##  Config Keys

| Key | Type | Default | Purpose |
|-----|------|---------|---------|
| `MIN_BODY_TEXT_LEN` | int | 200 | Min article length |
| `MAX_CHUNK_TOKENS` | int | 600 | Max tokens/chunk |
| `CHUNK_OVERLAP_TOKENS` | int | 50 | Overlap tokens |
| `BOILERPLATE_HEADING_PATTERNS` | list | [...] | Footer heading patterns |
| `BOILERPLATE_PHRASE_REGEXES` | list | [...] | Phrase patterns to remove |

---

##  Code Examples

### Use chunks cho embedding

```python
import json
from openai import OpenAI

client = OpenAI()

with open("chunks.jsonl") as f:
    for i, line in enumerate(f):
        if i >= 100:  # Process first 100
            break
        
        chunk = json.loads(line)
        
        # Embed text
        resp = client.embeddings.create(
            model="text-embedding-3-small",
            input=chunk["text"]
        )
        
        embedding = resp.data[0].embedding
        print(f"Chunk {chunk['chunk_id']}: {len(embedding)} dims")
```

### Analyze audit results

```python
import json
from collections import Counter

issues = Counter()

with open("audit_report.jsonl") as f:
    for line in f:
        chunk = json.loads(line)
        issues.update(chunk["issues"])

for issue, count in issues.most_common():
    print(f"{issue}: {count}")
```

### List all markdown files

```bash
ls -1 docs/ | head -20
find docs/ -name "*.md" | wc -l
```

---

##  Tips

1. **Start small**: Test với 10-20 articles trước (edit config để increase `MIN_BODY_TEXT_LEN`)
2. **Check audit**: Luôn kiểm tra `audit_report.jsonl` để xem chunk quality
3. **Adjust tokens**: Nếu chunks quá dài, giảm `MAX_CHUNK_TOKENS`
4. **Version control**: Git ignore: `docs/`, `chunks.jsonl`, `audit_report.jsonl`
5. **Backup**: Lưu lại `chunks.jsonl` trước khi chạy lại pipeline (overwrites)

---

##  Next Steps

1. [ ] Run `python3 main.py`
2. [ ] Check output: `ls docs/` `head chunks.jsonl`
3. [ ] Review audit: `cat audit_report.jsonl`
4. [ ] Adjust config if needed
5. [ ] Embed chunks into Vector DB
6. [ ] Build RAG application

---

**Last Updated**: 2024-07-03  
**Version**: 1.0
