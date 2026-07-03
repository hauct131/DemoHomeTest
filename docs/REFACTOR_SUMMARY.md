# Refactoring Summary - Clean Directory Layout & Path Centralization

**Date**: 2026-07-03  
**Status**: COMPLETED

## Overview

Following the target layout requirements, we have refactored the directory layout of the `DemoHomeTest` project. The business logic, algorithms, and formats are 100% preserved. The imports, configurations, and scripts have been updated to support running the pipeline end-to-end smoothly from any working directory.

---

## Directory Structure (Refactored)

The project now matches the requested target structure:

```
DemoHomeTest/
├── data/
│   └── optisigns_articles.json
│
├── output/
│   ├── articles/
│   ├── chunks.jsonl
│   ├── audit_report.jsonl
│   └── vector_store_state.json
│
├── scripts/
│   ├── crawl.py
│   ├── upload_vector_store.py
│   ├── verify_vector_store.py
│   └── cleanup_duplicate_files.py
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── utils.py
│   ├── html_cleaner.py
│   ├── markdown_converter.py
│   ├── chunking.py
│   ├── audit.py
│   ├── pipeline.py
│   └── vector_store.py
│
├── tests/
│   └── test_vector_store_upload.py
│
├── docs/
│   └── [placeholder/documentation]
│
├── main.py
├── requirements.txt
└── .gitignore
```

---

## Summary of Moves & Renames

| Original Path | New Path | Description |
| :--- | :--- | :--- |
| `optisigns_articles.json` | `data/optisigns_articles.json` | Moved raw input JSON. |
| `docs/*.md` | `output/articles/*.md` | Moved all generated markdown articles. |
| `chunks.jsonl` | `output/chunks.jsonl` | Moved pipeline output chunks file. |
| `audit_report.jsonl` | `output/audit_report.jsonl` | Moved pipeline audit report file. |
| `vector_store_state.json` | `output/vector_store_state.json` | Moved vector store upload state tracking file. |
| `crawl.py` | `scripts/crawl.py` | Moved data crawler helper script. |
| `upload_vector_store.py` | `scripts/upload_vector_store.py` | Moved OpenAI upload helper script. |
| `verify_vector_store.py` | `scripts/verify_vector_store.py` | Moved OpenAI store verification helper script. |
| `cleanup_duplicate_files.py` | `scripts/cleanup_duplicate_files.py` | Moved duplication cleanup helper script. |
| `src/html_cleaning.py` | `src/html_cleaner.py` | Renamed module for consistency. |
| `src/markdown_conversion.py` | `src/markdown_converter.py` | Renamed module for consistency. |

---

## Key Updates

### 1. Renaming and Internal Imports
- Renamed `src/html_cleaning.py` to `src/html_cleaner.py` and `src/markdown_conversion.py` to `src/markdown_converter.py`.
- Updated all references and imports inside `src/pipeline.py`, `src/audit.py`, and the scripts to use the new names correctly.

### 2. Path Centralization in `src/config.py`
- Defined absolute path references using the resolved project root (`Path(__file__).resolve().parent.parent`).
- Centralized all file paths:
  - `INPUT_JSON_PATH` -> `data/optisigns_articles.json`
  - `OUTPUT_DOCS_PATH` -> `output/articles/`
  - `OUTPUT_CHUNKS_PATH` -> `output/chunks.jsonl`
  - `OUTPUT_AUDIT_PATH` -> `output/audit_report.jsonl`
  - `VECTOR_STORE_STATE_PATH` -> `output/vector_store_state.json`
- Preserved string variables (`INPUT_JSON`, `OUTPUT_DOCS_DIR`, `OUTPUT_CHUNKS_JSONL`, `OUTPUT_AUDIT_JSONL`) pointing to the string versions of the new paths for backward compatibility.

### 3. Safe Execution Context for Scripts
- Modified the helper scripts inside `scripts/` (`crawl.py`, `upload_vector_store.py`, `verify_vector_store.py`, `cleanup_duplicate_files.py`) by resolving the project root dynamically and adding it to `sys.path`.
- This ensures scripts run successfully using `python3 scripts/<name>.py` from the root or any subdirectory without encountering `ModuleNotFoundError`.

### 4. GitIgnore Updates
- Updated `.gitignore` to ignore the entire `output/` directory (which contains generated articles, chunks, audit report, and vector store state files) instead of the old `docs/` and individual file levels.

### 5. `build.py`
- Left untouched per rule 6 because it contains the entire legacy monolithic pipeline logic (does not simply delegate to `src.pipeline`).

---

## Verification
- Ran existing tests successfully (`venv/bin/python3 -m tests.test_vector_store_upload`).
- Executed `main.py` successfully and verified it generated all files in `output/` and `output/articles/` directory cleanly.
- Verified that `verify_vector_store.py` runs successfully and retrieves store data correctly.

## Potential Breaking Changes
- Scripts running outside this folder structure that hardcode the path `"docs"` or `"chunks.jsonl"` relative to their execution directory will need to point to `"output/articles"` and `"output/chunks.jsonl"`. By using `src/config.py`, all project scripts are fully insulated from this change.
