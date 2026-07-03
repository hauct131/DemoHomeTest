"""
Audit chất lượng chunks: phát hiện vấn đề, tạo báo cáo.
"""

import json
import re
import hashlib
from collections import Counter, defaultdict
from typing import List, Dict
from pathlib import Path

from .utils import count_tokens
from . import config


# ============================================================
# BOILERPLATE CÒN SÓT (không bị 3 tầng regex trong markdown_converter
# bắt hết, vì đây là các cụm ngắn nằm XEN GIỮA nội dung thật, không
# đứng riêng thành 1 heading/paragraph để tầng 1-2 xóa nguyên khối)
# ============================================================
LEFTOVER_BOILERPLATE_PATTERNS: list[str] = [
    r"\byou'?re\s+all\s+set\b",
    r"\bthat'?s\s+it\b",
    r"\bthat'?s\s+all\b",
    r"\bfeel\s+free\s+to\s+reach\s+out\b",
    r"\blet\s+us\s+know\s+if\s+you\s+have\s+(?:any\s+)?questions?\b",
    r"\bhappy\s+signing\b",
]


def _normalize_for_dedup(text: str) -> str:
    """
    Chuẩn hóa text để so khớp duplicate: bỏ hết markdown syntax, số liệu
    thay đổi (id, ngày), khoảng trắng thừa, chuyển thường.

    Args:
        text: Chunk text

    Returns:
        Chuỗi normalized dùng để hash so trùng
    """
    t = text.lower()
    t = re.sub(r"!\[.*?\]\(.*?\)", "", t)          # images
    t = re.sub(r"\[image[^\]]*\]", "", t)            # image placeholder
    t = re.sub(r"https?://\S+", "", t)                # urls
    t = re.sub(r"#{1,6}\s*", "", t)                   # heading markers
    t = re.sub(r"[^a-z0-9\s]", "", t)                 # markdown punctuation
    t = re.sub(r"\s+", " ", t).strip()
    return t


def find_duplicate_chunks(chunks: List[Dict]) -> Dict[str, List[str]]:
    """
    Phát hiện chunk trùng lặp / gần trùng lặp trên TOÀN BỘ corpus.

    Dùng exact-match trên nội dung đã normalize (bỏ markdown syntax, URL,
    ảnh) - đủ để bắt các trường hợp phổ biến nhất trong support docs:
    đoạn cảnh báo/table/note bị lặp lại y hệt ở nhiều bài khác nhau.

    Args:
        chunks: Toàn bộ danh sách chunk (đã enrich metadata)

    Returns:
        {chunk_id: [other_chunk_ids_trung_voi_no]} - chỉ gồm chunk có ít
        nhất 1 bản trùng
    """
    groups: Dict[str, List[str]] = defaultdict(list)

    for c in chunks:
        normalized = _normalize_for_dedup(c["text"])
        # Bỏ qua chunk quá ngắn khi normalize (dễ trùng ngẫu nhiên, không đáng gắn cờ)
        if len(normalized) < 40:
            continue
        h = hashlib.md5(normalized.encode("utf-8")).hexdigest()
        groups[h].append(c["chunk_id"])

    duplicates: Dict[str, List[str]] = {}
    for ids in groups.values():
        if len(ids) > 1:
            for cid in ids:
                duplicates[cid] = [x for x in ids if x != cid]

    return duplicates


def audit_chunk(text: str) -> List[str]:
    """
    Kiểm tra chunk có vấn đề gì (rule-based).
    
    Trả về danh sách vấn đề phát hiện được. Có thể có false positive nhẹ
    ở ranh giới, nhưng đủ tốt để rà soát thủ công.
    
    Issues phát hiện:
        - orphan_heading: Chunk chỉ có heading, gần như không có nội dung
        - starts_mid_sentence: Chunk bắt đầu giữa câu (chữ thường)
        - ends_mid_list: Chunk kết thúc giữa danh sách
        - broken_code_block: Code block bị mở mà không đóng (số ``` lẻ)
        - starts_mid_table: Chunk bắt đầu với dòng table nhưng không có header
        - too_short: Quá ngắn (< 15 tokens)
        - too_long: Quá dài (> 1.5x max_tokens)
        - oversized_code_block: Chunk là 1 code block nguyên khối vượt quá
          max_tokens (ngoại lệ có chủ đích - xem split_oversized_unit)
        - possible_boilerplate_leftover: Có cụm boilerplate ngắn còn sót
          (không đứng riêng thành heading/paragraph nên 2 tầng regex trước
          không bắt được)
        - low_information_density: Chunk phần lớn là markdown syntax
          (link/table/ảnh placeholder), rất ít nội dung chữ thực sự
    
    Args:
        text: Chunk text
        
    Returns:
        List các issue code (string), empty nếu không có vấn đề
    """
    issues = []
    stripped = text.strip()
    
    if not stripped:
        return issues
    
    # 1. Orphan heading: chunk chỉ có heading mà gần như không có nội dung
    body_after_heading = re.sub(
        r"^#{1,6}\s+.+$",
        "",
        stripped,
        count=1,
        flags=re.MULTILINE
    ).strip()
    
    if re.match(r"^#{1,6}\s+", stripped) and len(body_after_heading) < 20:
        issues.append("orphan_heading")
    
    # 2. Starts mid-sentence: ký tự đầu tiên là chữ thường
    #    (không phải heading/list/code/quote) -> khả năng bị cắt ngang
    first_line = stripped.split("\n", 1)[0].strip()
    if first_line and not re.match(r"^[#\-*\d`>|!\[]", first_line):
        if first_line[0].islower() and not first_line.startswith("..."):
            issues.append("starts_mid_sentence")
    
    # 3. Ends mid-list: dòng cuối là bullet/số nhưng có vẻ dở dang
    last_line = stripped.split("\n")[-1].strip()
    if re.match(r"^[\-*]\s*$|^\d+\.\s*$", last_line):
        issues.append("ends_mid_list")
    
    # 4. Broken code block: số lượng ``` là lẻ (mở mà không đóng)
    fence_count = len(re.findall(r"^```", stripped, flags=re.MULTILINE))
    if fence_count % 2 != 0:
        issues.append("broken_code_block")
    
    # 5. Starts mid-table: chunk bắt đầu với | nhưng không có header sep
    lines = [l for l in stripped.split("\n") if l.strip()]
    if lines and lines[0].strip().startswith("|"):
        has_header_sep = any(
            re.match(r"^\|?[\s:|-]+\|$", l.strip())
            for l in lines[:3]
        )
        if not has_header_sep:
            issues.append("starts_mid_table")
    
    # 6. Too short: < 15 tokens
    tok = count_tokens(stripped)
    if tok < config.MIN_CHUNK_TOKENS:
        issues.append("too_short")
    
    # 7. Too long / oversized code block
    if tok > config.MAX_CHUNK_TOKENS * config.MAX_CHUNK_TOKENS_THRESHOLD:
        is_pure_code_block = bool(re.match(r"^```[\s\S]*```\s*$", stripped))
        if is_pure_code_block:
            issues.append("oversized_code_block")
        else:
            issues.append("too_long")

    # 8. Boilerplate còn sót (cụm ngắn nằm giữa nội dung thật)
    for pat in LEFTOVER_BOILERPLATE_PATTERNS:
        if re.search(pat, stripped, flags=re.IGNORECASE):
            issues.append("possible_boilerplate_leftover")
            break

    # 9. Low information density: phần lớn là markdown syntax, ít chữ thật
    text_only = re.sub(r"!\[.*?\]\(.*?\)", "", stripped)   # images
    text_only = re.sub(r"\[image[^\]]*\]", "", text_only, flags=re.IGNORECASE)
    text_only = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text_only)  # links -> giữ label
    text_only = re.sub(r"[#*`|>_-]", "", text_only)
    word_chars = len(re.sub(r"\s", "", text_only))
    total_chars = max(len(stripped), 1)
    if tok >= config.MIN_CHUNK_TOKENS and (word_chars / total_chars) < 0.35:
        issues.append("low_information_density")

    return issues


def run_audit(
    chunks: List[Dict],
    report_path: Path | str
) -> Dict:
    """
    Chạy audit trên tất cả chunks, tạo báo cáo JSON.
    
    Args:
        chunks: List các chunk dict (từ pipeline)
        report_path: Đường dẫn output report (jsonl)
        
    Returns:
        Dict với thống kê audit:
            {
                "total_chunks": int,
                "flagged_chunks": int,
                "flagged_percentage": float,
                "issue_counts": {issue_code: count},
                "report_path": str
            }
    """
    report_path = Path(report_path)
    
    issue_counter: Counter = Counter()
    flagged = []

    # Duplicate detection chạy corpus-wide (không phải per-chunk như audit_chunk)
    duplicate_map = find_duplicate_chunks(chunks)

    for c in chunks:
        issues = audit_chunk(c["text"])
        if c["chunk_id"] in duplicate_map:
            issues = issues + ["duplicate_content"]

        if issues:
            issue_counter.update(issues)
            entry = {
                **c,
                "issues": issues,
            }
            if c["chunk_id"] in duplicate_map:
                entry["duplicate_of"] = duplicate_map[c["chunk_id"]]
            flagged.append(entry)
    
    # Ghi báo cáo JSONL
    with open(report_path, "w", encoding="utf-8") as f:
        for item in flagged:
            row = {
                "chunk_id": item["chunk_id"],
                "article_title": item["article_title"],
                "source_url": item["source_url"],
                "issues": item["issues"],
                "text_preview": item["text"][:200],
            }
            if "duplicate_of" in item:
                row["duplicate_of"] = item["duplicate_of"]
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    
    # Tính thống kê
    total = len(chunks)
    flagged_count = len(flagged)
    flagged_pct = (flagged_count / total * 100) if total > 0 else 0
    
    # In kết quả
    print("\n" + "=" * 60)
    print("AUDIT CHẤT LƯỢNG CHUNK")
    print("=" * 60)
    print(f"Tổng chunks: {total}")
    print(f"Chunks có ít nhất 1 vấn đề: {flagged_count} ({flagged_pct:.1f}%)")
    print("\nBảng thống kê issues:")
    for issue, count in issue_counter.most_common():
        pct = (count / total * 100) if total > 0 else 0
        print(f"  {issue:25s}: {count:4d} ({pct:5.1f}%)")
    print(f"\nChi tiết từng chunk lỗi: {report_path}")
    print("=" * 60)
    
    return {
        "total_chunks": total,
        "flagged_chunks": flagged_count,
        "flagged_percentage": flagged_pct,
        "issue_counts": dict(issue_counter),
        "report_path": str(report_path),
    }