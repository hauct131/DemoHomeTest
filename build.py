"""
Pipeline: optisigns_articles.json (Zendesk Help Center dump)
           -> docs/*.md (đã làm sạch, chunk sẵn, có front-matter)
           -> chunks.jsonl (dùng thẳng để embed vào vector DB)

Chạy:
    python3 build.py

Yêu cầu thư viện:
    pip install beautifulsoup4 lxml markdownify tiktoken --break-system-packages

Lưu ý: KHÔNG cần cài package "slugify" hay "python-slugify" nữa — hàm slugify()
đã được tự viết trong file này để tránh xung đột tên module giữa 2 package đó
(package "slugify" cũ chỉ chạy Python 2, dùng unicode() gây lỗi ở Python 3).
"""

import json
import re
import os
from pathlib import Path
from collections import Counter

from bs4 import BeautifulSoup
from markdownify import markdownify as md


def slugify(text: str) -> str:
    """Tự viết, tránh xung đột với package 'slugify' (Python2-only) trùng tên
    module với 'python-slugify'. Không phụ thuộc thư viện ngoài."""
    import unicodedata
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")  # bỏ dấu tiếng Việt/Unicode
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "untitled"

try:
    import tiktoken
    _enc = tiktoken.get_encoding("cl100k_base")
    def count_tokens(text: str) -> int:
        return len(_enc.encode(text))
except Exception:
    def count_tokens(text: str) -> int:
        # fallback thô: ~4 ký tự/token
        return max(1, len(text) // 4)


# ============================================================
# CẤU HÌNH
# ============================================================
INPUT_JSON = "optisigns_articles.json"
OUTPUT_DOCS_DIR = "docs"
OUTPUT_CHUNKS_JSONL = "chunks.jsonl"
OUTPUT_AUDIT_JSONL = "audit_report.jsonl"
MIN_BODY_TEXT_LEN = 200   # bỏ bài có text ngắn hơn ngưỡng này (rỗng / "coming soon")
MAX_CHUNK_TOKENS = 600
CHUNK_OVERLAP_TOKENS = 50
BASE_URL = "https://support.optisigns.com/hc/en-us/articles/"

# --- TẦNG 1: block heading footer thật sự -> xóa nguyên khối
BOILERPLATE_HEADING_PATTERNS = [
    r"^need\s*help\b",
    r"^contact\s*us\b",
    r"^related\b",
    r"^more\s*guides?\b",
    r"^still\s*need\s*help\b",
    r"^if\s*you\s*have\s*any\s*(?:additional\s*)?questions\b",  # heading biến thể
]

# --- TẦNG 2: đoạn quảng cáo cố định. Có 2 biến thể xác nhận từ dữ liệu thật:
#   (a) "OptiSigns is a/the leader in [digital signage software]...<email>"
#   (b) "If you have any additional questions...feedback about OptiSigns,
#        feel free to reach out to our (support|billing) team at <email>"
#   Email có 2 dạng: support@optisigns.com và billing@optisigns.com (xác nhận
#   bằng cách quét toàn bộ 404 bài, không còn dạng nào khác) -> dùng regex
#   tổng quát [\w.-]+@optisigns\.com thay vì liệt kê từng địa chỉ.
EMAIL_ANY_REGEX = r"[\w.\-]+@optisigns\.com"

BOILERPLATE_AD_PARAGRAPH_REGEXES = [
    r"OptiSigns is (?:a|the) leader in \[digital signage software\.?\][\s\S]*?"
    r"\[?" + EMAIL_ANY_REGEX + r"\]?(?:\(mailto:[^)]*\))?\.?",
    r"If you have any additional questions,?\s*(?:concerns?,?\s*)?or any feedback about OptiSigns"
    r"[\s\S]*?\[?" + EMAIL_ANY_REGEX + r"\]?(?:\(mailto:[^)]*\))?\.?",
]

# Email lẻ còn sót ngoài 2 pattern trên (ví dụ mục "Reporting a security
# issue") -> chỉ xóa phần link, giữ câu xung quanh vì có thể là nội dung thật
EMAIL_LINK_REGEX = r"\[?" + EMAIL_ANY_REGEX + r"\]?(?:\(mailto:" + EMAIL_ANY_REGEX + r"\))?"

# --- TẦNG 3: cụm "That's all!" / "That's it!" / "Congratulations!" đứng riêng
#     (chỉ xóa CỤM TỪ, KHÔNG xóa nội dung phía sau -> vì nhiều bài dùng cụm
#     này như câu chuyển ý giữa bài, phía sau vẫn là nội dung thật, ví dụ:
#     "**That's all!**\n\nOnce OptiSigns AI detection is running, you'll notice...")
BOILERPLATE_PHRASE_REGEXES = [
    r"\*{0,2}that'?s\s*all\s*!?\*{0,2}\s*(?:congratulations?!?\*{0,2})?\s*",
    r"\*{0,2}that'?s\s*it\s*!?\*{0,2}\s*",
]

BOILERPLATE_INLINE_REGEXES = BOILERPLATE_AD_PARAGRAPH_REGEXES + BOILERPLATE_PHRASE_REGEXES

TAGS_TO_STRIP = ["script", "style", "iframe", "svg", "button",
                  "nav", "footer", "header", "aside", "form", "noscript"]


# ============================================================
# BƯỚC 1-2: LOAD + LÀM SẠCH HTML
# ============================================================
def load_articles(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def strip_unwanted_tags(soup: BeautifulSoup):
    for tag_name in TAGS_TO_STRIP:
        for tag in soup.find_all(tag_name):
            tag.decompose()
    return soup


def strip_internal_toc(soup: BeautifulSoup):
    """Xóa <ul> đầu bài nếu TOÀN BỘ <a> bên trong trỏ tới anchor nội bộ (#...)."""
    body_root = soup.body if soup.body else soup
    first_elements = body_root.find_all(recursive=False)
    if not first_elements:
        return soup
    first = first_elements[0]
    if first.name == "ul":
        links = first.find_all("a", href=True)
        if links and all(a["href"].startswith("#") for a in links):
            first.decompose()
    return soup


def strip_anchor_targets(soup: BeautifulSoup):
    """Xóa các <a name="..."></a> rỗng dùng làm điểm neo cho TOC đã xóa."""
    for a in soup.find_all("a", attrs={"name": True}):
        if not a.get_text(strip=True):
            a.decompose()
    return soup

def replace_images_with_placeholder(html_str: str) -> str:
    """Thay mọi thẻ <img> bằng văn bản [Image: tên-file] để không mất dấu vết."""
    soup = BeautifulSoup(html_str, "lxml")
    for img in soup.find_all("img"):
        src = img.get("src", "")
        # Lấy phần cuối cùng của URL làm tên file
        filename = src.rsplit("/", 1)[-1].split("?")[0] if src else "unknown"
        # Tạo alt nếu có, nếu không thì dùng tên file
        alt = img.get("alt", "").strip()
        placeholder = f"[Image: {alt or filename}]"
        img.replace_with(placeholder)  # thay thẻ <img> bằng text
    return str(soup)


def clean_html(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html or "", "lxml")
    soup = strip_unwanted_tags(soup)
    soup = strip_internal_toc(soup)
    soup = strip_anchor_targets(soup)
    return str(soup)


# ============================================================
# BƯỚC 3: HTML -> MARKDOWN
# ============================================================
def html_to_markdown(clean_html_str: str) -> str:
    return md(clean_html_str, heading_style="ATX", bullets="-")


# ============================================================
# BƯỚC 4: CHUẨN HÓA MARKDOWN
# ============================================================
def normalize_heading_text(raw_heading: str) -> str:
    """Bỏ markdown bold (**), emoji, dấu câu thừa, chuẩn hóa apostrophe cong ' -> ',
    để so khớp heading boilerplate bất kể biến thể trình bày."""
    text = raw_heading.strip()
    text = text.strip("#").strip()
    text = re.sub(r"\*+", "", text)          # bỏ ** bold **
    text = text.replace("\u2019", "'")        # ’ -> '
    text = text.lower().strip()
    return text


def is_boilerplate_heading(raw_heading: str) -> bool:
    normalized = normalize_heading_text(raw_heading)
    return any(re.match(pat, normalized) for pat in BOILERPLATE_HEADING_PATTERNS)


def strip_boilerplate_sections(markdown_text: str) -> str:
    """Xóa NGUYÊN KHỐI heading (## hoặc ###) + nội dung bên trong nếu heading đó
    là boilerplate. Chạy TRƯỚC chunking để chunk không bao giờ dính footer."""
    # Tách theo mọi heading level 2-3, giữ lại phần preamble trước heading đầu tiên
    blocks = re.split(r"(?=^#{2,3}\s)", markdown_text, flags=re.MULTILINE)
    kept = []
    for block in blocks:
        heading_match = re.match(r"^(#{2,3})\s+(.+)$", block, flags=re.MULTILINE)
        if heading_match and is_boilerplate_heading(heading_match.group(2)):
            continue  # bỏ toàn bộ block này
        kept.append(block)
    return "".join(kept)


def strip_inline_boilerplate(text: str) -> str:
    for pat in BOILERPLATE_AD_PARAGRAPH_REGEXES:
        text = re.sub(pat, "", text, flags=re.IGNORECASE)
    # Email lẻ còn sót (không thuộc câu quảng cáo trên, ví dụ mục "Reporting a
    # security issue") -> chỉ xóa phần link, GIỮ câu xung quanh vì có thể vẫn
    # là hướng dẫn thật (không phải quảng cáo thuần túy)
    text = re.sub(EMAIL_LINK_REGEX, "our support team", text, flags=re.IGNORECASE)
    for pat in BOILERPLATE_PHRASE_REGEXES:
        text = re.sub(pat, "", text, flags=re.IGNORECASE)
    return text


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+\n", "\n", text)          # trailing spaces
    text = re.sub(r"\n{3,}", "\n\n", text)           # >2 dòng trống -> 1 dòng trống
    text = re.sub(r"[ \t]{2,}", " ", text)            # nhiều space liên tiếp
    return text.strip()

def shorten_urls(text: str, max_url_len=80) -> str:
    """Giữ nguyên text hiển thị, nhưng thay URL dài bằng [text](link) để giảm token."""
    def repl(m):
        full = m.group(0)
        link_text = m.group(1)
        url = m.group(2)
        if len(url) > max_url_len:
            return f'[{link_text}](link)'   # giữ nguyên text, thay URL thật bằng placeholder
        return full
    return re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)', repl, text)

def normalize_markdown(text: str) -> str:
    text = strip_boilerplate_sections(text)   # xóa nguyên block heading footer
    text = strip_inline_boilerplate(text)     # dọn phần lạc ra ngoài (nếu có)
    text = re.sub(r'!\[.*?\]\((data:image/[^)]+)\)', '[Image omitted]', text)
    text = shorten_urls(text)
    text = normalize_whitespace(text)
    return text


# ============================================================
# BƯỚC 5: REWRITE INTERNAL LINKS (2-PASS)
# ============================================================
def build_id_to_slug_map(articles) -> dict:
    mapping = {}
    for a in articles:
        slug = slugify(a["title"]) + ".md"
        mapping[a["id"]] = slug
    return mapping


def rewrite_internal_links(clean_html_str: str, id_to_slug: dict) -> str:
    soup = BeautifulSoup(clean_html_str, "lxml")
    for a_tag in soup.find_all("a", href=True):
        m = re.search(r"/articles/(\d+)(-[^/#]*)?(?:#.*)?$", a_tag["href"])
        if m:
            article_id = int(m.group(1))
            if article_id in id_to_slug:
                a_tag["href"] = id_to_slug[article_id]
    return str(soup)


# ============================================================
# BƯỚC 7: METADATA (front-matter)
# ============================================================
def build_front_matter(article: dict, slug: str) -> str:
    lines = [
        "---",
        f'title: "{article["title"].replace(chr(34), chr(39))}"',
        f'source_url: "{article["html_url"]}"',
        f'article_id: {article["id"]}',
        f'section_id: {article.get("section_id")}',
        f'created_at: "{article.get("created_at")}"',
        f'updated_at: "{article.get("updated_at")}"',
        f'labels: {json.dumps(article.get("label_names") or [])}',
        "---",
        "",
    ]
    return "\n".join(lines)


# ============================================================
# BƯỚC 8: CHUNKING (theo heading, có overlap khi quá dài)
# ============================================================
def split_by_heading(markdown_text: str):
    """Chia theo heading cấp 2 (##). Nếu không có ## nào, trả nguyên văn."""
    parts = re.split(r"(?=^##\s)", markdown_text, flags=re.MULTILINE)
    return [p for p in parts if p.strip()]


def split_long_text(text: str, max_tokens: int, overlap_tokens: int):
    """Chia nhỏ theo đoạn văn (paragraph), giữ overlap giữa các chunk.
    Code block (```...```) luôn được coi là 1 khối nguyên vẹn, không bao giờ
    bị tách ngang dù bên trong có dòng trống (ví dụ code GraphQL nhiều dòng)."""
    # Bước 1: tách text thành các đoạn xen kẽ [text thường, code block, text thường, ...]
    # re.split với group bắt (```...```) sẽ giữ lại code block nguyên vẹn trong kết quả
    segments = re.split(r"(```[\s\S]*?```)", text)

    atomic_units = []
    for seg in segments:
        if seg.startswith("```") and seg.endswith("```"):
            atomic_units.append(seg)  # code block -> 1 đơn vị nguyên vẹn
        else:
            atomic_units.extend(p for p in re.split(r"\n\s*\n", seg) if p.strip())

    chunks = []
    current, current_tokens = [], 0

    for unit in atomic_units:
        u_tokens = count_tokens(unit)
        if current_tokens + u_tokens > max_tokens and current:
            chunks.append("\n\n".join(current))
            # overlap: giữ lại đơn vị cuối của chunk trước làm phần mở đầu chunk sau
            # (không overlap bằng chính code block để tránh lặp code không cần thiết)
            overlap_text = current[-1] if current and not current[-1].startswith("```") else ""
            current = [overlap_text] if overlap_text and count_tokens(overlap_text) <= overlap_tokens else []
            current_tokens = count_tokens(overlap_text) if current else 0
        current.append(unit)
        current_tokens += u_tokens

    if current:
        chunks.append("\n\n".join(current))
    return chunks

def is_heading_only(text: str) -> bool:
    """Trả về True nếu chunk chỉ chứa một heading và không có nội dung thực sự."""
    stripped = text.strip()
    if not re.match(r'^#{1,6}\s', stripped):
        return False
    # Xóa dòng heading đầu tiên
    rest = re.sub(r'^#{1,6}\s+.+$', '', stripped, count=1, flags=re.MULTILINE).strip()
    # Loại bỏ các thành phần không phải văn bản (ảnh, chú thích ảnh, dòng kẻ ngang)
    rest = re.sub(r'!\[.*?\]\(.*?\)', '', rest)
    rest = re.sub(r'\[Image[^\]]*\]', '', rest)
    rest = re.sub(r'^-{3,}$', '', rest, flags=re.MULTILINE)
    # Nếu sau khi làm sạch, văn bản còn lại rất ngắn (<20 ký tự) thì coi là heading rỗng
    return len(rest.strip()) < 20

def is_junk_chunk(text: str) -> bool:
    """True nếu chunk không mang nội dung thật: chỉ có '---', heading trơ trọi
    (không kèm câu chữ), hoặc bảng rỗng không có dữ liệu."""
    stripped = text.strip()
    # bỏ hết heading markers, hr, khoảng trắng, ký tự bảng rỗng để xem còn lại gì
    residual = re.sub(r"^#{1,6}\s*$", "", stripped, flags=re.MULTILINE)
    residual = re.sub(r"^-{3,}$", "", residual, flags=re.MULTILINE)
    residual = re.sub(r"^\|[\s|]*\|$", "", residual, flags=re.MULTILINE)
    residual = re.sub(r"^\|?[\s:|-]+\|$", "", residual, flags=re.MULTILINE)
    residual = residual.strip()
    return count_tokens(residual) < 15 


def chunk_markdown(markdown_text: str, title: str, max_tokens=MAX_CHUNK_TOKENS,
                    overlap=CHUNK_OVERLAP_TOKENS):
    # Xóa ảnh base64 (vô nghĩa cho embedding) để tránh chunk phình to
    markdown_text = re.sub(r'!\[.*?\]\((data:image/[^)]+)\)', '[Image]', markdown_text)

    sections = split_by_heading(markdown_text)
    final_chunks = []
    for sec in sections:
        heading_match = re.match(r"^##\s+(.+)$", sec, flags=re.MULTILINE)
        heading = heading_match.group(1).strip() if heading_match else title
        if count_tokens(sec) <= max_tokens:
            candidates = [sec.strip()]
        else:
            candidates = split_long_text(sec, max_tokens, overlap)
        for sub in candidates:
            sub = sub.strip()
            if sub and not is_junk_chunk(sub) and not is_heading_only(sub):
                final_chunks.append({"heading": heading, "text": sub})

    # ===== HẬU XỬ LÝ: NỐI CHUNK BỊ CẮT GIỮA CÂU =====
    merged_chunks = []
    for i, chunk in enumerate(final_chunks):
        text = chunk["text"]
        first_line = text.split("\n")[0].strip()
        # Nếu chunk bắt đầu bằng chữ thường & không có ký hiệu đặc biệt → dấu hiệu bị cắt
        if i > 0 and first_line and not re.match(r'^[#\-*\d`>|!\[]', first_line) and first_line[0].islower():
            prev_text = merged_chunks[-1]["text"]
            combined = prev_text + "\n\n" + text
            # Nối nếu tổng token không vượt quá 130% max_tokens
            if count_tokens(combined) <= max_tokens * 1.3:
                merged_chunks[-1]["text"] = combined
                continue
            else:
                # Không nối được → thêm dấu "..." để đánh dấu phần tiếp nối
                text = "... " + text
                chunk["text"] = text
        merged_chunks.append(chunk)

    return merged_chunks

# ============================================================
# AUDIT: kiểm tra chất lượng chunk sau khi build xong
# ============================================================
def audit_chunk(text: str) -> list:
    """Trả về danh sách vấn đề phát hiện được trong 1 chunk (rule-based, có thể
    có false positive nhẹ ở ranh giới, nhưng đủ tốt để rà soát thủ công)."""
    issues = []

    stripped = text.strip()

    # 1. Heading mồ côi: chunk chỉ có heading, gần như không có nội dung
    body_after_heading = re.sub(r"^#{1,6}\s+.+$", "", stripped, count=1, flags=re.MULTILINE).strip()
    if re.match(r"^#{1,6}\s+", stripped) and len(body_after_heading) < 20:
        issues.append("orphan_heading")

    # 2. Chunk bắt đầu giữa câu: ký tự đầu tiên là chữ thường và KHÔNG phải
    #    heading/list/code/table/quote -> khả năng cao bị cắt giữa câu
    first_line = stripped.split("\n", 1)[0].strip()
    if first_line and not re.match(r"^[#\-*\d`>|!\[]", first_line):
        if first_line[0].islower() and not first_line.startswith("..."):  # <-- thêm điều kiện này
            issues.append("starts_mid_sentence")

    # 3. Chunk kết thúc giữa danh sách: dòng cuối là bullet/số nhưng có vẻ dở dang
    #    (rất ngắn, không có dấu câu kết thúc) hoặc kết thúc bằng dấu ':'
    last_line = stripped.split("\n")[-1].strip()
    if re.match(r"^[\-*]\s*$|^\d+\.\s*$", last_line):
        issues.append("ends_mid_list")

    # 4. Code block bị cắt: số lượng ``` là số lẻ -> chưa đóng
    fence_count = len(re.findall(r"^```", stripped, flags=re.MULTILINE))
    if fence_count % 2 != 0:
        issues.append("broken_code_block")

    # 5. Table bị cắt: chunk BẮT ĐẦU bằng dòng table (|...|) nhưng KHÔNG có
    #    dòng header phân cách (| --- | --- |) trong chunk -> table đã bắt đầu
    #    ở chunk trước, bị cắt ngang. (Lưu ý: dòng CUỐI bắt đầu bằng "|" là
    #    bình thường với mọi bảng markdown hợp lệ, không phải dấu hiệu bị cắt.)
    lines = [l for l in stripped.split("\n") if l.strip()]
    if lines and lines[0].strip().startswith("|"):
        has_header_sep = any(re.match(r"^\|?[\s:|-]+\|$", l.strip()) for l in lines[:3])
        if not has_header_sep:
            issues.append("starts_mid_table")

    # 6. Quá ngắn / quá dài bất thường
    tok = count_tokens(stripped)
    if tok < 15:
        issues.append("too_short")
    if tok > MAX_CHUNK_TOKENS * 1.5:
        issues.append("too_long")

    return issues


def run_audit(chunks: list, report_path: str):
    from collections import Counter
    issue_counter = Counter()
    flagged = []
    for c in chunks:
        issues = audit_chunk(c["text"])
        if issues:
            issue_counter.update(issues)
            flagged.append({**c, "issues": issues})

    with open(report_path, "w", encoding="utf-8") as f:
        for item in flagged:
            f.write(json.dumps({
                "chunk_id": item["chunk_id"],
                "article_title": item["article_title"],
                "source_url": item["source_url"],
                "issues": item["issues"],
                "text_preview": item["text"][:200],
            }, ensure_ascii=False) + "\n")

    print(f"\n=== AUDIT CHẤT LƯỢNG CHUNK ===")
    print(f"Tổng chunk có ít nhất 1 vấn đề: {len(flagged)} / {len(chunks)} "
          f"({len(flagged)/len(chunks)*100:.1f}%)")
    for issue, n in issue_counter.most_common():
        print(f"  - {issue}: {n}")
    print(f"Chi tiết từng chunk lỗi đã ghi vào: {report_path}")


# ============================================================
# MAIN PIPELINE
# ============================================================
def main():
    Path(OUTPUT_DOCS_DIR).mkdir(parents=True, exist_ok=True)
    articles = load_articles(INPUT_JSON)
    print(f"Tổng số bài viết: {len(articles)}")

    # Lọc bài rỗng / quá ngắn (dùng plain text để đo, không tính tag HTML)
    filtered = []
    skipped_empty = 0
    for a in articles:
        raw = a.get("body") or ""
        plain = BeautifulSoup(raw, "lxml").get_text(" ", strip=True)
        if len(plain) < MIN_BODY_TEXT_LEN:
            skipped_empty += 1
            continue
        filtered.append(a)
    print(f"Bỏ qua {skipped_empty} bài rỗng/quá ngắn (< {MIN_BODY_TEXT_LEN} ký tự)")
    print(f"Còn lại: {len(filtered)} bài để xử lý")

    # Dedup theo title trùng y hệt (giữ bản updated_at mới nhất)
    by_title = {}
    for a in filtered:
        t = a["title"].strip().lower()
        if t not in by_title or a["updated_at"] > by_title[t]["updated_at"]:
            by_title[t] = a
    dedup_articles = list(by_title.values())
    if len(dedup_articles) != len(filtered):
        print(f"Loại bỏ {len(filtered) - len(dedup_articles)} bài trùng title, giữ bản mới nhất")

    id_to_slug = build_id_to_slug_map(dedup_articles)

    all_chunks = []
    seen_slugs = Counter()

    for a in dedup_articles:
        raw_html = a.get("body") or ""

        cleaned = clean_html(raw_html)
        cleaned = rewrite_internal_links(cleaned, id_to_slug)

        cleaned = replace_images_with_placeholder(cleaned)
        markdown_body = html_to_markdown(cleaned)

        markdown_body = html_to_markdown(cleaned)
        markdown_body = normalize_markdown(markdown_body)

        slug = id_to_slug[a["id"]]
        seen_slugs[slug] += 1
        if seen_slugs[slug] > 1:
            # tránh ghi đè file nếu 2 title slugify trùng nhau
            slug = slug.replace(".md", f"-{a['id']}.md")

        front_matter = build_front_matter(a, slug)
        full_md = front_matter + f"# {a['title']}\n\n" + markdown_body

        out_path = os.path.join(OUTPUT_DOCS_DIR, slug)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full_md)

        # Chunk cho vector DB
        chunks = chunk_markdown(markdown_body, a["title"])
        for i, c in enumerate(chunks):
            all_chunks.append({
                "chunk_id": f"{a['id']}-{i}",
                "article_id": a["id"],
                "article_title": a["title"],
                "heading": c["heading"],
                "source_url": a["html_url"],
                "section_id": a.get("section_id"),
                "updated_at": a.get("updated_at"),
                "labels": a.get("label_names") or [],
                "text": c["text"],
                "token_count": count_tokens(c["text"]),
            })

    with open(OUTPUT_CHUNKS_JSONL, "w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"\nĐã ghi {len(dedup_articles)} file markdown vào: {OUTPUT_DOCS_DIR}")
    print(f"Đã ghi {len(all_chunks)} chunks vào: {OUTPUT_CHUNKS_JSONL}")
    print(f"Trung bình {len(all_chunks)/len(dedup_articles):.1f} chunks/bài")

    run_audit(all_chunks, OUTPUT_AUDIT_JSONL)


if __name__ == "__main__":
    main()

