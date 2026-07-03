"""
Cấu hình toàn bộ pipeline: đường dẫn, ngưỡng token, pattern boilerplate, v.v.
"""

from pathlib import Path


# ============================================================
# ĐƯỜNG DẪN FILE
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# QUAN TRỌNG: Railway volume được mount vào PROJECT_ROOT/"data" (xem log
# "Saved -> /app/data/optisigns_articles.json"). Mọi file cần PERSIST giữa
# các lần chạy/deploy (đặc biệt là vector_store_state.json - dùng để delta
# upload) BẮT BUỘC phải nằm trong "data/", KHÔNG được để ở "output/" vì
# "output/" không nằm trong volume và sẽ bị xoá sạch mỗi lần container
# restart/redeploy -> gây ra hiện tượng "chạy lại từ đầu" trên Railway dù
# local vẫn chạy tiếp được bình thường.
DATA_DIR: Path = PROJECT_ROOT / "data"

INPUT_JSON_PATH: Path = DATA_DIR / "optisigns_articles.json"
OUTPUT_DOCS_PATH: Path = DATA_DIR / "output" / "articles"
OUTPUT_CHUNKS_PATH: Path = DATA_DIR / "output" / "chunks.jsonl"
OUTPUT_AUDIT_PATH: Path = DATA_DIR / "output" / "audit_report.jsonl"
VECTOR_STORE_STATE_PATH: Path = DATA_DIR / "vector_store_state.json"

# Giữ lại các biến cũ dạng chuỗi để tương thích ngược nếu cần
INPUT_JSON: str = str(INPUT_JSON_PATH)
OUTPUT_DOCS_DIR: str = str(OUTPUT_DOCS_PATH)
OUTPUT_CHUNKS_JSONL: str = str(OUTPUT_CHUNKS_PATH)
OUTPUT_AUDIT_JSONL: str = str(OUTPUT_AUDIT_PATH)


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

# TẦNG 3: Cụm "That's all!" / "That's it!" / "Congratulations!" +
# các câu CTA lặp lại kiểu "feel free to reach out..." / "let us know if you
# have questions..." nằm XEN GIỮA nội dung thật (không đứng riêng thành
# heading/paragraph nên tầng 1-2 không xóa được nguyên khối).
#
# Chỉ xóa TỪ cụm trigger ĐẾN HẾT CÂU (dấu chấm/xuống dòng gần nhất), KHÔNG
# xóa cả câu, để giữ lại phần thông tin thật đứng trước (vd: "We also accept
# Purchase Orders—feel free to reach out for a quote." -> giữ lại "We also
# accept Purchase Orders", chỉ xóa phần CTA phía sau).
BOILERPLATE_PHRASE_REGEXES: list[str] = [
    r"\*{0,2}that'?s\s*all\s*!?\*{0,2}\s*(?:congratulations?!?\*{0,2})?\s*",
    r"\*{0,2}that'?s\s*it\s*!?\*{0,2}\s*",
    r"[—\-:,]?\s*\*{0,2}feel\s+free\s+to\s+reach\s+out\b[^.\n]*\.?",
    r"[—\-:,]?\s*\*{0,2}(?:please\s+)?let\s+us\s+know\s+if\s+you\s+have\s+"
    r"(?:any\s+)?questions?(?:\s+or\s+feedback)?[^.\n]*\.?",
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