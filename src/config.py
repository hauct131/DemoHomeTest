"""
Cấu hình toàn bộ pipeline: đường dẫn, ngưỡng token, pattern boilerplate, v.v.
"""

from pathlib import Path


# ============================================================
# ĐƯỜNG DẪN FILE
# ============================================================
INPUT_JSON: str = "optisigns_articles.json"
OUTPUT_DOCS_DIR: str = "docs"
OUTPUT_CHUNKS_JSONL: str = "chunks.jsonl"
OUTPUT_AUDIT_JSONL: str = "audit_report.jsonl"

# Chuyển đổi string thành Path objects cho dễ dàng sử dụng
INPUT_JSON_PATH: Path = Path(INPUT_JSON)
OUTPUT_DOCS_PATH: Path = Path(OUTPUT_DOCS_DIR)
OUTPUT_CHUNKS_PATH: Path = Path(OUTPUT_CHUNKS_JSONL)
OUTPUT_AUDIT_PATH: Path = Path(OUTPUT_AUDIT_JSONL)


# ============================================================
# NGƯỠNG LỌC + CHUNK
# ============================================================
MIN_BODY_TEXT_LEN: int = 200  # Bỏ bài có text ngắn hơn (rỗng / "coming soon")
MAX_CHUNK_TOKENS: int = 600   # Token tối đa mỗi chunk
CHUNK_OVERLAP_TOKENS: int = 50  # Token overlap giữa chunks


# ============================================================
# BASE URL
# ============================================================
BASE_URL: str = "https://support.optisigns.com/hc/en-us/articles/"


# ============================================================
# BOILERPLATE PATTERNS
# ============================================================

# TẦNG 1: Heading footer thật sự -> xóa nguyên khối
BOILERPLATE_HEADING_PATTERNS: list[str] = [
    r"^need\s*help\b",
    r"^contact\s*us\b",
    r"^related\b",
    r"^more\s*guides?\b",
    r"^still\s*need\s*help\b",
    r"^if\s*you\s*have\s*any\s*(?:additional\s*)?questions\b",
]

# TẦNG 2: Đoạn quảng cáo cố định
EMAIL_ANY_REGEX: str = r"[\w.\-]+@optisigns\.com"

BOILERPLATE_AD_PARAGRAPH_REGEXES: list[str] = [
    r"OptiSigns is (?:a|the) leader in \[digital signage software\.?\][\s\S]*?"
    r"\[?" + EMAIL_ANY_REGEX + r"\]?(?:\(mailto:[^)]*\))?\.?",
    r"If you have any additional questions,?\s*(?:concerns?,?\s*)?or any feedback about OptiSigns"
    r"[\s\S]*?\[?" + EMAIL_ANY_REGEX + r"\]?(?:\(mailto:[^)]*\))?\.?",
]

# TẦNG 3: Cụm "That's all!" / "That's it!" / "Congratulations!"
BOILERPLATE_PHRASE_REGEXES: list[str] = [
    r"\*{0,2}that'?s\s*all\s*!?\*{0,2}\s*(?:congratulations?!?\*{0,2})?\s*",
    r"\*{0,2}that'?s\s*it\s*!?\*{0,2}\s*",
]

BOILERPLATE_INLINE_REGEXES: list[str] = BOILERPLATE_AD_PARAGRAPH_REGEXES + BOILERPLATE_PHRASE_REGEXES


# ============================================================
# HTML CLEANING
# ============================================================
TAGS_TO_STRIP: list[str] = [
    "script", "style", "iframe", "svg", "button",
    "nav", "footer", "header", "aside", "form", "noscript"
]


# ============================================================
# AUDIT & QUALITY
# ============================================================
MIN_CHUNK_TOKENS: int = 15  # Chunk quá ngắn
MAX_CHUNK_TOKENS_THRESHOLD: float = 1.5  # 1.5x max_tokens = quá dài
HEADING_ONLY_MIN_CHARS: int = 20  # Threshold xác định heading rỗng
