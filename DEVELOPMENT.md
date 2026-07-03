# Development Guide - OptiSigns RAG Pipeline

Hướng dẫn dành cho developers muốn mở rộng, tùy chỉnh, hoặc đóng góp vào project.

## Mục Lục

1. [Architecture Overview](#architecture-overview)
2. [Code Structure](#code-structure)
3. [Adding New Features](#adding-new-features)
4. [Type Hints & Documentation](#type-hints--documentation)
5. [Testing](#testing)
6. [Code Style](#code-style)
7. [Debugging](#debugging)
8. [Performance Tips](#performance-tips)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    main.py (Entry Point)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│               pipeline.py (Orchestrator)                 │
│  - Load articles từ JSON                                │
│  - Coordinate từng step của pipeline                    │
│  - Manage file I/O                                      │
└────────────────┬────────────────┬───────────────────────┘
                 │                │
        ┌────────▼──────┐  ┌──────▼─────────┐
        │ HTML Cleaning  │  │ Markdown       │
        │ Processing     │  │ Conversion     │
        │                │  │ & Cleanup      │
        │ • strip tags   │  │                │
        │ • strip TOC    │  │ • normalize    │
        │ • replace img  │  │ • rm boilerp   │
        │ • rewrite link │  │ • shorten URL  │
        └────────┬───────┘  └────────┬───────┘
                 │                   │
        ┌────────▼──────────────────▼──────┐
        │      Chunking Pipeline            │
        │  • split_by_heading               │
        │  • split_long_text                │
        │  • is_heading_only, is_junk       │
        │  • merge mid-sentence chunks      │
        └────────┬──────────────────────────┘
                 │
        ┌────────▼──────────────────┐
        │   Quality Audit            │
        │  • detect orphan headings  │
        │  • detect mid-sentence     │
        │  • detect broken code      │
        │  • generate report         │
        └────────┬──────────────────┘
                 │
    ┌────────────▼────────────┐
    │    Output Generation    │
    ├────────────┬────────────┤
    │ docs/*.md  │ chunks.    │ audit_
    │ (markdown) │ jsonl      │ report.jsonl
    └────────────┴────────────┘
```

---

## Code Structure

### Module: `config.py`
**Trách nhiệm**: Tập trung tất cả constants

```python
# Thêm constant mới
MY_NEW_THRESHOLD = 100

# Thêm pattern regex mới
MY_PATTERNS = [r"pattern1", r"pattern2"]
```

### Module: `utils.py`
**Trách nhiệm**: Utility functions (không state, pure functions)

```python
def my_utility_function(text: str) -> str:
    """
    Docstring đầy đủ.
    
    Args:
        text: Description
        
    Returns:
        Description
        
    Raises:
        ValueError: Description
    """
    # Implementation
    return result
```

### Module: `html_cleaning.py`
**Trách nhiệm**: Tất cả công việc liên quan HTML processing

```python
def my_html_processor(html: str) -> str:
    """Process HTML theo cách mới."""
    soup = BeautifulSoup(html, "lxml")
    # ... processing ...
    return str(soup)
```

### Module: `markdown_conversion.py`
**Trách nhiệm**: HTML -> Markdown, normalization, boilerplate removal

```python
def my_markdown_normalization(md: str) -> str:
    """Chuẩn hóa markdown theo quy tắc mới."""
    # ... processing ...
    return normalized_md
```

### Module: `chunking.py`
**Trách nhiệm**: Chia markdown thành chunks

```python
def my_chunking_strategy(text: str) -> List[str]:
    """Chia text theo strategy mới."""
    # ... chunking logic ...
    return chunks
```

### Module: `audit.py`
**Trách nhiệm**: Quality checks, audit reports

```python
def my_audit_rule(chunk: str) -> List[str]:
    """Detect issue mới trong chunk."""
    issues = []
    # ... checking logic ...
    return issues
```

### Module: `pipeline.py`
**Trách nhiệm**: Điều phối toàn bộ pipeline

```python
def run_pipeline(...) -> Dict:
    """Main orchestration."""
    # 1. Load
    # 2. Filter
    # 3. Process
    # 4. Audit
    # 5. Output
    return stats
```

---

## Adding New Features

### Example 1: Thêm Boilerplate Pattern Mới

```python
# 1. Định nghĩa pattern trong config.py
# src/config.py

BOILERPLATE_HEADING_PATTERNS.append(r"^my new footer\b")

BOILERPLATE_PHRASE_REGEXES.append(
    r"custom phrase to remove"
)

# 2. Pattern sẽ được dùng tự động bởi normalize_markdown()
# Không cần thay đổi markdown_conversion.py!
```

### Example 2: Thêm Audit Rule Mới

```python
# 1. Thêm hàm trong audit.py
# src/audit.py

def check_external_links(chunk: str) -> List[str]:
    """Phát hiện chunk có quá nhiều external links."""
    issues = []
    external_link_count = len(re.findall(r'http', chunk))
    
    if external_link_count > 5:
        issues.append("too_many_external_links")
    
    return issues

# 2. Tích hợp vào audit_chunk()
# Sửa hàm audit_chunk() để gọi check_external_links()

def audit_chunk(text: str) -> List[str]:
    issues = []
    # ... existing checks ...
    issues.extend(check_external_links(text))  # NEW
    return issues
```

### Example 3: Custom Metadata Field

```python
# 1. Thêm enrichment logic trong pipeline.py
# src/pipeline.py

def enrich_chunk_metadata(chunk: Dict, article: Dict) -> Dict:
    """Thêm metadata custom."""
    chunk["priority"] = "high" if article.get("views", 0) > 1000 else "low"
    chunk["language"] = detect_language(chunk["text"])
    return chunk

# 2. Gọi trong process_article()
chunks_with_meta = []
for i, c in enumerate(chunks):
    chunk_obj = {
        "chunk_id": f"{article['id']}-{i}",
        # ... existing fields ...
    }
    chunk_obj = enrich_chunk_metadata(chunk_obj, article)  # NEW
    chunks_with_meta.append(chunk_obj)
```

### Example 4: Custom HTML Cleaning

```python
# 1. Thêm hàm trong html_cleaning.py
# src/html_cleaning.py

def remove_custom_elements(soup: BeautifulSoup) -> BeautifulSoup:
    """Xóa elements theo custom rule."""
    for elem in soup.find_all(class_="ad-banner"):
        elem.decompose()
    return soup

# 2. Tích hợp vào clean_html()
def clean_html(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html or "", "lxml")
    soup = strip_unwanted_tags(soup)
    soup = strip_internal_toc(soup)
    soup = remove_custom_elements(soup)  # NEW
    soup = strip_anchor_targets(soup)
    return str(soup)
```

### Example 5: Filter Pipeline Stage Mới

```python
# 1. Thêm filter function trong pipeline.py
# src/pipeline.py

def filter_by_custom_criteria(articles: List[Dict]) -> Tuple[List[Dict], int]:
    """Lọc articles theo criteria custom."""
    filtered = []
    skipped = 0
    
    for a in articles:
        # Ví dụ: bỏ articles có quá nhiều links
        link_count = a["body"].count("<a")
        if link_count < 50:
            filtered.append(a)
        else:
            skipped += 1
    
    return filtered, skipped

# 2. Thêm vào run_pipeline()
def run_pipeline(...) -> Dict:
    # ... existing code ...
    
    # Existing filters
    filtered, skipped_empty = filter_empty_articles(articles, MIN_BODY_TEXT_LEN)
    dedup_articles, dedup_count = dedup_articles_by_title(filtered)
    
    # NEW filter
    final_articles, skipped_links = filter_by_custom_criteria(dedup_articles)
    
    # ... rest of pipeline ...
```

---

## Type Hints & Documentation

### Best Practices

####  Good: Full Type Hints

```python
def process_markdown(
    text: str,
    max_tokens: int = 600,
    patterns: list[str] | None = None
) -> Dict[str, Any]:
    """
    Process markdown with type hints.
    
    Args:
        text: Input markdown
        max_tokens: Maximum tokens per chunk
        patterns: Optional regex patterns (default: config patterns)
        
    Returns:
        Dict with keys:
            - chunks: List of processed chunks
            - stats: Processing statistics
            
    Raises:
        ValueError: If max_tokens <= 0
        TypeError: If text is not string
    """
    if not isinstance(text, str):
        raise TypeError("text must be string")
    
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")
    
    # Implementation
    return {"chunks": [...], "stats": {...}}
```

####  Bad: No Type Hints

```python
def process_markdown(text, max_tokens=600, patterns=None):
    """Process markdown."""
    # Ambiguous: what's the return type?
    # what if text is None?
    # ...
    return result
```

### Type Hints Guidelines

```python
# Scalar types
def process_text(text: str) -> str: ...
def count_items(items: list) -> int: ...
def get_probability() -> float: ...

# Optional (has default None)
def process(data: str | None = None) -> str: ...

# Union types (one of)
def get_value(key: str | int) -> str | int: ...

# Collection types
def process_list(items: list[str]) -> list[dict]: ...
def process_dict(data: dict[str, int]) -> dict[str, list]: ...

# Custom types
def enrich_chunk(chunk: Dict[str, Any]) -> Dict[str, Any]: ...

# Callable
def apply_function(func: Callable[[str], str], text: str) -> str:
    return func(text)

# Tuple
def split_text(text: str) -> tuple[str, str]:
    parts = text.split()
    return parts[0], " ".join(parts[1:])

# Generic (for library functions)
from typing import List, Dict, Optional, Callable, Tuple

def process(items: List[str], processor: Callable[[str], str]) -> Dict[str, str]:
    return {item: processor(item) for item in items}
```

---

## Testing

### Unit Tests

```python
# tests/test_utils.py

import unittest
from src.utils import slugify, count_tokens

class TestUtils(unittest.TestCase):
    def test_slugify(self):
        """Test slug generation."""
        self.assertEqual(slugify("How to Install"), "how-to-install")
        self.assertEqual(slugify("My **Title**"), "my-title")
        
    def test_count_tokens(self):
        """Test token counting."""
        self.assertGreater(count_tokens("hello world"), 0)
        self.assertGreater(
            count_tokens("hello world" * 100),
            count_tokens("hello world")
        )

if __name__ == "__main__":
    unittest.main()
```

### Run Tests

```bash
# Run all tests
python3 -m unittest discover -s tests -p "test_*.py"

# Run specific test
python3 -m unittest tests.test_utils.TestUtils.test_slugify

# With verbose
python3 -m unittest discover -s tests -p "test_*.py" -v
```

---

## Code Style

### PEP 8 Compliance

```bash
# Install linter
pip3 install --break-system-packages flake8 black

# Check style
flake8 src/

# Auto-format
black src/
```

### Naming Conventions

```python
# Constants: UPPERCASE_WITH_UNDERSCORES
MAX_CHUNK_TOKENS = 600
BOILERPLATE_PATTERNS = [...]

# Functions/variables: lowercase_with_underscores
def process_markdown(text: str) -> str: ...
chunk_counter = 0

# Classes: PascalCase
class ArticleProcessor:
    pass

# Private: _leading_underscore
def _internal_helper() -> None: ...
```

### Docstring Format

```python
"""
Short one-line summary ending with period.

Longer description if needed. Can span multiple
paragraphs explaining the function in detail.

Args:
    param1: Description
    param2: Description (type: str, optional)
    
Returns:
    Description of return value
    
Raises:
    ValueError: When something is invalid
    FileNotFoundError: When file is missing
    
Examples:
    >>> slugify("My Title")
    'my-title'
    
    >>> count_tokens("hello world")
    2
"""
```

---

## Debugging

### Print Debugging

```python
# Simple print
print(f"Debug: article_id={article_id}, chunks={len(chunks)}")

# Pretty print
import json
print(json.dumps(chunk, indent=2, ensure_ascii=False))

# Conditional debug
DEBUG = True
if DEBUG:
    print(f"Processing: {article['title']}")
```

### Python Debugger (pdb)

```python
import pdb

def problematic_function():
    x = 10
    pdb.set_trace()  # Execution pauses here
    y = x + 5
    return y

# Run: python3 -m pdb src/pipeline.py
# Commands: n (next), s (step), c (continue), p x (print), l (list)
```

### Logging (Better than print)

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_article(article):
    logger.info(f"Processing: {article['id']}")
    try:
        # ... processing ...
    except Exception as e:
        logger.error(f"Error processing {article['id']}: {e}", exc_info=True)
```

---

## Performance Tips

### 1. Profile Code Execution

```python
import cProfile
import pstats

# Profile function
cProfile.run("run_pipeline()", "pipeline_stats")

# View results
stats = pstats.Stats("pipeline_stats")
stats.sort_stats("cumulative").print_stats(10)  # Top 10 slowest
```

### 2. Optimize Token Counting

```python
# Current: O(n) per chunk
for chunk in chunks:
    tokens = count_tokens(chunk["text"])  # Repeated calculation

# Better: O(1) if pre-computed
all_chunks = []
for chunk in chunks_raw:
    chunk["token_count"] = count_tokens(chunk["text"])
    all_chunks.append(chunk)
```

### 3. Batch File Operations

```python
# Slow: Write mỗi chunk ngay
for chunk in chunks:
    with open("chunks.jsonl", "a") as f:
        f.write(json.dumps(chunk) + "\n")

# Fast: Batch write
buffer = []
for chunk in chunks:
    buffer.append(chunk)
    if len(buffer) >= 100:
        with open("chunks.jsonl", "a") as f:
            for c in buffer:
                f.write(json.dumps(c) + "\n")
        buffer = []
```

### 4. Use Generators for Large Data

```python
# Memory inefficient: Load all into list
def load_all_chunks():
    chunks = []
    for article in articles:
        chunks.extend(chunk_markdown(article))
    return chunks

# Memory efficient: Yield one by one
def load_chunks_generator():
    for article in articles:
        for chunk in chunk_markdown(article):
            yield chunk
```

---

## Common Patterns

### Pattern 1: Optional Processing

```python
def process_with_optional_step(
    articles: List[Dict],
    include_audit: bool = True
) -> Dict:
    """Process articles with optional audit step."""
    
    # Mandatory steps
    filtered = filter_empty_articles(articles)
    chunks = chunk_all_articles(filtered)
    
    # Optional steps
    if include_audit:
        audit_stats = run_audit(chunks)
        return {"chunks": chunks, "audit": audit_stats}
    
    return {"chunks": chunks}
```

### Pattern 2: Pipeline with Checkpoints

```python
def run_pipeline_with_checkpoints():
    """Pipeline với intermediate checkpoints."""
    
    # Checkpoint 1: Load
    articles = load_articles("articles.json")
    
    # Checkpoint 2: Filter
    filtered = filter_empty_articles(articles)
    dump_checkpoint("filtered_articles.json", filtered)
    
    # Checkpoint 3: Process
    # Có thể load từ checkpoint nếu bị lỗi
    if Path("processed_markdown.json").exists():
        processed = load_checkpoint("processed_markdown.json")
    else:
        processed = process_all_articles(filtered)
        dump_checkpoint("processed_markdown.json", processed)
    
    # Checkpoint 4: Chunk
    chunks = chunk_all_articles(processed)
    return chunks
```

---

## Contributing Guidelines

### Code Review Checklist

- [ ] Type hints on all functions
- [ ] Docstrings on all public functions
- [ ] No hardcoded values (use config.py)
- [ ] Error handling with try/except
- [ ] PEP 8 compliant (run flake8)
- [ ] Tests written
- [ ] Documentation updated

---

**Version**: 1.0  
**Last Updated**: 2024-07-03
