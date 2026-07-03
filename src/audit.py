"""
Audit chất lượng chunks: phát hiện vấn đề, tạo báo cáo.
"""

import json
import re
from collections import Counter
from typing import List, Dict
from pathlib import Path

from .utils import count_tokens
from . import config


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
    
    # 7. Too long: > 1.5x max_tokens
    if tok > config.MAX_CHUNK_TOKENS * config.MAX_CHUNK_TOKENS_THRESHOLD:
        issues.append("too_long")
    
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
    
    for c in chunks:
        issues = audit_chunk(c["text"])
        if issues:
            issue_counter.update(issues)
            flagged.append({
                **c,
                "issues": issues
            })
    
    # Ghi báo cáo JSONL
    with open(report_path, "w", encoding="utf-8") as f:
        for item in flagged:
            f.write(json.dumps({
                "chunk_id": item["chunk_id"],
                "article_title": item["article_title"],
                "source_url": item["source_url"],
                "issues": item["issues"],
                "text_preview": item["text"][:200],
            }, ensure_ascii=False) + "\n")
    
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
