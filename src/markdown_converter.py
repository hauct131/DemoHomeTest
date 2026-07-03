"""
Chuyển đổi HTML sang Markdown, chuẩn hóa Markdown, loại bỏ boilerplate.
"""

import re
from markdownify import markdownify as md

from . import config


def html_to_markdown(clean_html_str: str) -> str:
    """
    Chuyển đổi cleaned HTML sang Markdown.
    
    Args:
        clean_html_str: HTML string (đã được clean)
        
    Returns:
        Markdown string
    """
    return md(clean_html_str, heading_style="ATX", bullets="-")


def normalize_heading_text(raw_heading: str) -> str:
    """
    Chuẩn hóa heading text để so khớp boilerplate patterns.
    
    Loại bỏ:
    - Markdown bold (**text**)
    - Emoji
    - Apostrophe cong ' thành '
    - Chuyển thường
    
    Args:
        raw_heading: Raw heading text (ví dụ "## My **Heading**")
        
    Returns:
        Normalized heading (ví dụ "my heading")
    """
    text = raw_heading.strip()
    # Bỏ các ký tự heading (#, ##, ###, ...)
    text = text.strip("#").strip()
    # Bỏ markdown bold (**)
    text = re.sub(r"\*+", "", text)
    # Chuẩn hóa apostrophe cong ' -> '
    text = text.replace("\u2019", "'")
    # Chuyển thường
    text = text.lower().strip()
    return text


def is_boilerplate_heading(raw_heading: str) -> bool:
    """
    Kiểm tra heading có phải là boilerplate footer (Need Help, Contact Us, v.v.).
    
    Args:
        raw_heading: Raw heading text
        
    Returns:
        True nếu là boilerplate heading
    """
    normalized = normalize_heading_text(raw_heading)
    return any(re.match(pat, normalized) for pat in config.BOILERPLATE_HEADING_PATTERNS)


def strip_boilerplate_sections(markdown_text: str) -> str:
    """
    Xóa NGUYÊN KHỐI heading (## hoặc ###) + nội dung bên trong
    nếu heading đó là boilerplate.
    
    Chạy TRƯỚC chunking để chunk không bao giờ dính footer/ads.
    
    Args:
        markdown_text: Markdown string
        
    Returns:
        Markdown string sau khi xóa boilerplate sections
    """
    # Tách markdown theo mọi heading level 2-3
    # Dùng lookahead ((?=^#{2,3}\s)) để giữ lại heading trong mỗi block
    blocks = re.split(r"(?=^#{2,3}\s)", markdown_text, flags=re.MULTILINE)
    
    kept = []
    for block in blocks:
        # Check heading đầu tiên của block
        heading_match = re.match(r"^(#{2,3})\s+(.+)$", block, flags=re.MULTILINE)
        if heading_match and is_boilerplate_heading(heading_match.group(2)):
            # Bỏ toàn bộ block này
            continue
        kept.append(block)
    
    return "".join(kept)


def strip_inline_boilerplate(text: str) -> str:
    """
    Loại bỏ boilerplate inline (ads, email contact, v.v.) khỏi text.
    
    Pipeline:
        1. Xóa ad paragraphs (OptiSigns leader, contact us, etc.)
        2. Thay email links bằng "our support team"
        3. Xóa phrases ("That's all!", "That's it!", etc.)
    
    Args:
        text: Markdown text
        
    Returns:
        Text sau khi xóa boilerplate inline
    """
    # Xóa các ad paragraph đầy đủ
    for pat in config.BOILERPLATE_AD_PARAGRAPH_REGEXES:
        text = re.sub(pat, "", text, flags=re.IGNORECASE)
    
    # Xóa email link, giữ ngữ cảnh xung quanh
    # (vì email lẻ có thể là hướng dẫn thật, không phải ads)
    email_regex = config.EMAIL_ANY_REGEX
    text = re.sub(email_regex, "our support team", text, flags=re.IGNORECASE)
    
    # Xóa các phrase boilerplate
    for pat in config.BOILERPLATE_PHRASE_REGEXES:
        text = re.sub(pat, "", text, flags=re.IGNORECASE)
    
    return text


def normalize_markdown(markdown_text: str) -> str:
    """
    Chuẩn hóa markdown: xóa boilerplate, base64 images, shorten URLs, v.v.
    
    Pipeline:
        1. Xóa boilerplate sections (headings + content)
        2. Xóa inline boilerplate
        3. Xóa base64 images
        4. Rút gọn URLs dài
        5. Chuẩn hóa whitespace
    
    Args:
        markdown_text: Raw markdown string
        
    Returns:
        Normalized markdown string
    """
    from .utils import shorten_urls, normalize_whitespace
    
    # Xóa nguyên block heading footer
    markdown_text = strip_boilerplate_sections(markdown_text)
    # Xóa inline boilerplate
    markdown_text = strip_inline_boilerplate(markdown_text)
    # Xóa base64 images (không dùng được cho embedding)
    markdown_text = re.sub(
        r'!\[.*?\]\((data:image/[^)]+)\)',
        '[Image omitted]',
        markdown_text
    )
    # Rút gọn URLs dài
    markdown_text = shorten_urls(markdown_text)
    # Chuẩn hóa whitespace
    markdown_text = normalize_whitespace(markdown_text)
    
    return markdown_text
