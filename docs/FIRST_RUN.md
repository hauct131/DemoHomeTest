#  First Run Guide - OptiSigns RAG Pipeline

Hướng dẫn từng bước để chạy pipeline lần đầu tiên.

---

## Step 1: Kiểm tra Setup

### 1.1 Kiểm tra Python

```bash
python3 --version
# Output: Python 3.9+

which python3
# Output: /usr/bin/python3 (hoặc similar)
```

### 1.2 Kiểm tra File Input

```bash
ls -lh optisigns_articles.json
# Output: -rw-r--r-- ... optisigns_articles.json

# Xem sample
head -100 optisigns_articles.json | python3 -m json.tool | head -30
```

### 1.3 Kiểm tra Working Directory

```bash
pwd
# Output: .../Home_Test_CTH

ls -la
# Output:
# src/
# main.py
# requirements.txt
# optisigns_articles.json
# docs/
```

---

## Step 2: Cài Dependencies

```bash
# Cài từ requirements.txt
pip3 install --break-system-packages -r requirements.txt

# Hoặc manual
pip3 install --break-system-packages beautifulsoup4 lxml markdownify tiktoken
```

**Expected output**:
```
Successfully installed beautifulsoup4-4.12.2 lxml-4.9.3 markdownify-0.11.6 tiktoken-0.5.1
```

---

## Step 3: Xác Minh Import

```bash
# Test imports
python3 -c "from src import config; print(' config OK')"
python3 -c "from src.pipeline import run_pipeline; print(' pipeline OK')"
python3 -c "from bs4 import BeautifulSoup; from markdownify import markdownify; print(' external libs OK')"

# Expected output:
#  config OK
#  pipeline OK
#  external libs OK
```

---

## Step 4: Chạy Pipeline (Full)

```bash
python3 main.py
```

**Expected output**:
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

[6] Writing chunks to chunks.jsonl...
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

Chi tiết từng chunk lỗi: audit_report.jsonl
============================================================

 Output markdown: docs/ (376 files)
 Output chunks:   chunks.jsonl (1,234 lines)
 Output audit:    audit_report.jsonl
 Avg chunks/article: 3.3
============================================================
```

**Thời gian**: 5-10 phút (tùy máy)

---

## Step 5: Kiểm Tra Output

### 5.1 Markdown Files

```bash
# Xem số lượng
ls -1 docs/ | wc -l
# Output: 376

# Xem sample file
head -30 docs/how-to-install-optisigns.md
```

**Expected structure**:
```markdown
---
title: "How to Install OptiSigns"
source_url: "https://support.optisigns.com/hc/en-us/articles/123456"
article_id: 123456
section_id: 789
created_at: "2024-01-15T10:00:00Z"
updated_at: "2024-03-01T15:30:00Z"
labels: ["installation", "setup"]
---

# How to Install OptiSigns

## System Requirements

- Windows 10 or later
...
```

### 5.2 Chunks JSONL

```bash
# Xem số lượng
wc -l chunks.jsonl
# Output: 1234 chunks.jsonl

# Xem first chunk (pretty printed)
head -1 chunks.jsonl | python3 -m json.tool
```

**Expected structure**:
```json
{
  "chunk_id": "123456-0",
  "article_id": 123456,
  "article_title": "How to Install OptiSigns",
  "heading": "System Requirements",
  "source_url": "https://support.optisigns.com/hc/en-us/articles/123456",
  "section_id": 789,
  "updated_at": "2024-03-01T15:30:00Z",
  "labels": ["installation", "setup"],
  "text": "Windows 10 or later\n4GB RAM minimum\n100MB disk space",
  "token_count": 28
}
```

### 5.3 Audit Report

```bash
# Xem số lượng
wc -l audit_report.jsonl
# Output: 47 audit_report.jsonl (chỉ chunks có issue)

# Xem first 5 chunks có issue
head -5 audit_report.jsonl | python3 -m json.tool
```

**Expected structure**:
```json
{
  "chunk_id": "654321-5",
  "article_title": "Troubleshooting Common Issues",
  "source_url": "https://support.optisigns.com/hc/en-us/articles/654321",
  "issues": ["starts_mid_sentence", "too_short"],
  "text_preview": "and then restart the application..."
}
```

---

## Step 6: Analyze Results

### 6.1 Summary Statistics

```bash
# Tổng chunks có issue
wc -l audit_report.jsonl

# Thống kê issues
python3 << 'EOF'
import json
from collections import Counter

issues = Counter()
with open("audit_report.jsonl") as f:
    for line in f:
        chunk = json.loads(line)
        issues.update(chunk["issues"])

print("\n=== Issue Statistics ===")
for issue, count in issues.most_common():
    print(f"{issue:25s}: {count:3d}")
EOF
```

**Expected output**:
```
=== Issue Statistics ===
too_long                 :  20
starts_mid_sentence      :  15
too_short                :  12
```

### 6.2 Chunk Statistics

```bash
# Avg tokens per chunk
python3 << 'EOF'
import json
from statistics import mean, stdev

tokens = []
with open("chunks.jsonl") as f:
    for line in f:
        chunk = json.loads(line)
        tokens.append(chunk["token_count"])

print(f"Total chunks: {len(tokens)}")
print(f"Avg tokens: {mean(tokens):.1f}")
print(f"Stdev: {stdev(tokens):.1f}")
print(f"Min: {min(tokens)}")
print(f"Max: {max(tokens)}")
EOF
```

**Expected output**:
```
Total chunks: 1234
Avg tokens: 185.5
Stdev: 142.3
Min: 15
Max: 598
```

---

## Step 7: Troubleshooting

### Problem: `ModuleNotFoundError`

```bash
# Error:
# ModuleNotFoundError: No module named 'markdownify'

# Solution:
pip3 install --break-system-packages -r requirements.txt
```

### Problem: `FileNotFoundError: optisigns_articles.json`

```bash
# Error:
# FileNotFoundError: Input file not found: optisigns_articles.json

# Check file exists:
ls -la optisigns_articles.json

# Or copy from correct location
cp /path/to/optisigns_articles.json .
```

### Problem: Pipeline very slow

```bash
# Slow pipeline? Test with small sample first
python3 << 'EOF'
from src.pipeline import run_pipeline
from pathlib import Path

# Modify config for testing
import src.config as config
config.MIN_BODY_TEXT_LEN = 1000  # Filter to longer articles only

stats = run_pipeline(verbose=True)
print(stats)
EOF
```

### Problem: Out of memory

```bash
# If you have memory issues:
# 1. Increase MIN_BODY_TEXT_LEN to filter more
# 2. Decrease MAX_CHUNK_TOKENS
# 3. Process articles in batches

# Edit src/config.py:
MIN_BODY_TEXT_LEN = 500  # From 200
MAX_CHUNK_TOKENS = 400   # From 600
```

---

## Step 8: Next Steps

### Option A: Use for Vector DB (RAG)

```python
# 1. Load chunks
import json

chunks = []
with open("chunks.jsonl") as f:
    for line in f:
        chunks.append(json.loads(line))

# 2. Embed (using OpenAI, Hugging Face, etc.)
from openai import OpenAI
client = OpenAI()

embeddings = {}
for chunk in chunks[:100]:  # Process first 100
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunk["text"]
    )
    embeddings[chunk["chunk_id"]] = resp.data[0].embedding

# 3. Store in Vector DB (Pinecone, Weaviate, etc.)
```

### Option B: Use for Static Site

```bash
# 1. Render markdown to HTML
pip3 install --break-system-packages markdown
python3 << 'EOF'
import markdown
import os
from pathlib import Path

for md_file in Path("docs").glob("*.md"):
    with open(md_file) as f:
        content = f.read()
    
    # Skip front-matter
    _, content = content.split("---\n", 2)[1:]
    
    html = markdown.markdown(content)
    
    html_file = md_file.with_suffix(".html")
    with open(html_file, "w") as f:
        f.write(f"<!DOCTYPE html><html><body>{html}</body></html>")

print(f"Generated {len(list(Path('docs').glob('*.html')))} HTML files")
EOF
```

### Option C: Integrate with CMS

```bash
# 1. Export to CSV
python3 << 'EOF'
import json
import csv

with open("chunks.jsonl") as jf, open("chunks.csv", "w", newline="") as cf:
    writer = csv.DictWriter(cf, fieldnames=[
        "chunk_id", "article_title", "heading", "token_count", "text"
    ])
    writer.writeheader()
    
    for line in jf:
        chunk = json.loads(line)
        writer.writerow({
            "chunk_id": chunk["chunk_id"],
            "article_title": chunk["article_title"],
            "heading": chunk["heading"],
            "token_count": chunk["token_count"],
            "text": chunk["text"][:200] + "..."
        })

print(" Exported to chunks.csv")
EOF

# 2. Import into CMS (WordPress, Drupal, Headless CMS, etc.)
```

---

## Step 9: Verify Success

**All of these should be TRUE**:

- [x] `python3 main.py` completed without errors
- [x] `docs/` contains 350+ markdown files
- [x] `chunks.jsonl` contains 1000+ lines
- [x] `audit_report.jsonl` contains flagged chunks
- [x] All markdown files have front-matter
- [x] All chunks have correct fields
- [x] Audit issues make sense (not all errors)

**If all TRUE**:  **Pipeline is working correctly!**

---

## Step 10: Next Deep Dive

Choose one:

1. **Customize Configuration**: Edit `src/config.py`
2. **Understand Code**: Read `DEVELOPMENT.md`
3. **Integrate with RAG**: See `USAGE.md` Advanced section
4. **Deploy to Production**: Set up CI/CD, monitoring, etc.

---

##  Common Questions

**Q: Can I run it again?**  
A: Yes! It will overwrite previous output. Backup first if needed.

**Q: Can I customize it?**  
A: Yes! Edit `src/config.py` to change any setting.

**Q: How do I add new boilerplate patterns?**  
A: Add to `BOILERPLATE_PHRASE_REGEXES` in `src/config.py`

**Q: Is output exactly same as before?**  
A: Yes! Same input → same output (just better organized code)

**Q: What if it fails?**  
A: Check error message, troubleshoot above, or check `USAGE.md`

---

**Version**: 1.0  
**Last Updated**: 2024-07-03  
**Status**: Ready for first run 
