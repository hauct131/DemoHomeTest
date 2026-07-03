"""
Logic chia markdown thành chunks cho vector DB:
- split_by_heading: chia theo heading
- split_long_text: chia nhỏ khi quá dài
- is_heading_only: detect heading rỗng
- is_junk_chunk: detect chunk vô nghĩa
- chunk_markdown: pipeline chunking chính
"""

import re
from typing import List, Dict

from .utils import count_tokens
from . import config


def split_by_heading(markdown_text: str) -> List[str]:
    """
    Chia markdown theo heading cấp 2 (##).
    
    Nếu không có heading nào, trả nguyên văn.
    
    Args:
        markdown_text: Markdown string
        
    Returns:
        List các section (mỗi section bắt đầu bằng heading)
    """
    # Split theo ##, dùng lookahead để giữ lại ## trong result
    parts = re.split(r"(?=^##\s)", markdown_text, flags=re.MULTILINE)
    return [p for p in parts if p.strip()]


def split_long_text(
    text: str,
    max_tokens: int,
    overlap_tokens: int
) -> List[str]:
    """
    Chia nhỏ text dài thành chunks có token overlap.
    
    Code block (```...```) được coi là 1 khối nguyên vẹn, không bao giờ
    bị tách ngang dù bên trong có dòng trống.
    
    Algorithm:
        1. Tách text thành atomic units (paragraph hoặc code block)
        2. Xếp units vào chunks, nếu vượt max_tokens -> tạo chunk mới
        3. Giữ overlap bằng cách nhồi nhúng unit cuối của chunk trước
    
    Args:
        text: Text cần chia
        max_tokens: Token tối đa mỗi chunk
        overlap_tokens: Token overlap giữa chunks
        
    Returns:
        List các chunk (string)
    """
    # Tách text thành segments (xen kẽ [text thường, code block, text thường, ...])
    # Dùng group capturing () để giữ code blocks trong result
    segments = re.split(r"(```[\s\S]*?```)", text)
    
    # Chuyển segments thành atomic units
    atomic_units = []
    for seg in segments:
        if seg.startswith("```") and seg.endswith("```"):
            # Code block -> 1 đơn vị nguyên vẹn
            atomic_units.append(seg)
        else:
            # Text thường -> tách theo paragraph (dòng trống)
            for p in re.split(r"\n\s*\n", seg):
                if p.strip():
                    atomic_units.append(p)
    
    # Xếp units vào chunks
    chunks = []
    current: List[str] = []
    current_tokens = 0
    
    for unit in atomic_units:
        u_tokens = count_tokens(unit)
        
        # Nếu thêm unit này vượt max -> tạo chunk mới
        if current_tokens + u_tokens > max_tokens and current:
            chunks.append("\n\n".join(current))
            
            # Overlap: giữ lại đơn vị cuối của chunk trước (nếu không phải code block)
            overlap_text = ""
            if current and not current[-1].startswith("```"):
                overlap_text = current[-1]
                if count_tokens(overlap_text) > overlap_tokens:
                    overlap_text = ""
            
            current = [overlap_text] if overlap_text else []
            current_tokens = count_tokens(overlap_text) if overlap_text else 0
        
        current.append(unit)
        current_tokens += u_tokens
    
    # Xử lý chunk cuối
    if current:
        chunks.append("\n\n".join(current))
    
    return chunks


def is_heading_only(text: str) -> bool:
    """
    Kiểm tra chunk chỉ chứa heading và không có nội dung thực sự.
    
    Ví dụ:
        "## My Section" -> True
        "## My Section\n\nSome content" -> False
        "## My Section\n\n[Image: photo.jpg]" -> True (ảnh không tính nội dung)
    
    Args:
        text: Chunk text
        
    Returns:
        True nếu chunk chỉ là heading rỗng
    """
    stripped = text.strip()
    
    # Không phải heading -> False
    if not re.match(r'^#{1,6}\s', stripped):
        return False
    
    # Xóa heading đầu tiên
    rest = re.sub(r'^#{1,6}\s+.+$', '', stripped, count=1, flags=re.MULTILINE)
    rest = rest.strip()
    
    # Loại bỏ các thành phần không phải text thực sự
    rest = re.sub(r'!\[.*?\]\(.*?\)', '', rest)  # images
    rest = re.sub(r'\[Image[^\]]*\]', '', rest)  # image placeholders
    rest = re.sub(r'^-{3,}$', '', rest, flags=re.MULTILINE)  # horizontal rules
    
    # Nếu còn lại quá ít -> coi là heading rỗng
    return len(rest.strip()) < config.HEADING_ONLY_MIN_CHARS


def is_junk_chunk(text: str) -> bool:
    """
    Kiểm tra chunk có phải là junk (không có nội dung thực sự).
    
    Junk patterns:
        - Chỉ có dấu '---', heading trơ trọi, bảng rỗng
        - Quá ngắn (< 15 tokens)
    
    Args:
        text: Chunk text
        
    Returns:
        True nếu là junk chunk
    """
    stripped = text.strip()
    
    # Loại bỏ các ký tự/pattern không chứa nội dung thực sự
    residual = re.sub(r"^#{1,6}\s*$", "", stripped, flags=re.MULTILINE)
    residual = re.sub(r"^-{3,}$", "", residual, flags=re.MULTILINE)
    residual = re.sub(r"^\|[\s|]*\|$", "", residual, flags=re.MULTILINE)
    residual = re.sub(r"^\|?[\s:|-]+\|$", "", residual, flags=re.MULTILINE)
    
    residual = residual.strip()
    
    # Nếu quá ngắn -> junk
    return count_tokens(residual) < config.MIN_CHUNK_TOKENS


def chunk_markdown(
    markdown_text: str,
    title: str,
    max_tokens: int = config.MAX_CHUNK_TOKENS,
    overlap_tokens: int = config.CHUNK_OVERLAP_TOKENS
) -> List[Dict[str, str]]:
    """
    Pipeline chunking chính: chia markdown thành chunks cho vector DB.
    
    Pipeline:
        1. Xóa base64 images
        2. Chia theo heading cấp 2
        3. Với mỗi section:
            - Nếu vừa -> thêm vào chunks
            - Nếu dài -> tách nhỏ (giữ overlap)
        4. Lọc junk chunks, heading-only chunks
        5. Xử lý hậu: nối chunk bị cắt giữa câu
    
    Args:
        markdown_text: Markdown string
        title: Tiêu đề bài viết (fallback heading)
        max_tokens: Token tối đa mỗi chunk (default từ config)
        overlap_tokens: Token overlap (default từ config)
        
    Returns:
        List dict với key:
            - "heading": Heading của chunk (từ ##)
            - "text": Chunk text
    """
    # Bước 1: Xóa base64 images (không dùng được, làm phình chunk)
    markdown_text = re.sub(
        r'!\[.*?\]\((data:image/[^)]+)\)',
        '[Image]',
        markdown_text
    )
    
    # Bước 2: Chia theo heading cấp 2
    sections = split_by_heading(markdown_text)
    
    final_chunks = []
    
    # Bước 3-4: Xử lý từng section
    for sec in sections:
        # Trích heading (## My Heading)
        heading_match = re.match(r"^##\s+(.+)$", sec, flags=re.MULTILINE)
        heading = heading_match.group(1).strip() if heading_match else title
        
        # Kiểm tra kích thước section
        if count_tokens(sec) <= max_tokens:
            # Section vừa -> xem có thể thêm trực tiếp
            candidates = [sec.strip()]
        else:
            # Section dài -> tách nhỏ
            candidates = split_long_text(sec, max_tokens, overlap_tokens)
        
        # Lọc junk chunks, heading-only chunks
        for sub in candidates:
            sub = sub.strip()
            if sub and not is_junk_chunk(sub) and not is_heading_only(sub):
                final_chunks.append({
                    "heading": heading,
                    "text": sub
                })
    
    # Bước 5: Xử lý hậu - nối chunk bị cắt giữa câu
    merged_chunks = []
    
    for i, chunk in enumerate(final_chunks):
        text = chunk["text"]
        first_line = text.split("\n")[0].strip()
        
        # Heuristic: chunk bắt đầu bằng chữ thường + không có ký tự đặc biệt
        # -> khả năng cao bị cắt giữa câu
        is_mid_sentence = (
            i > 0
            and first_line
            and not re.match(r'^[#\-*\d`>|!\[]', first_line)
            and first_line[0].islower()
        )
        
        if is_mid_sentence:
            prev_text = merged_chunks[-1]["text"]
            combined = prev_text + "\n\n" + text
            
            # Nối nếu tổng token <= 130% max_tokens
            if count_tokens(combined) <= max_tokens * 1.3:
                merged_chunks[-1]["text"] = combined
                continue
            else:
                # Không nối được -> thêm "..." để đánh dấu mid-sentence
                text = "... " + text
                chunk["text"] = text
        
        merged_chunks.append(chunk)
    
    return merged_chunks
