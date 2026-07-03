"""
Các hàm tiện ích chung: slugify, count_tokens, normalize_whitespace, shorten_urls, v.v.
"""

import re
import unicodedata
from typing import Callable


def slugify(text: str) -> str:
    """
    Chuyển text thành slug an toàn cho tên file.
    
    Loại bỏ dấu tiếng Việt, Unicode, chuyển thường, 
    thay dấu cách bằng '-'.
    
    Args:
        text: Chuỗi input (có thể chứa Unicode, dấu, v.v.)
        
    Returns:
        Slug an toàn cho tên file (ví dụ: "my-title")
        
    Note:
        Hàm được tự viết để tránh xung đột package 'slugify' (Python2-only)
        và 'python-slugify'.
    """
    # Chuẩn hóa Unicode (NFKD = decompose)
    text = unicodedata.normalize("NFKD", text)
    # Bỏ dấu tiếng Việt bằng cách encode ASCII, ignore non-ASCII
    text = text.encode("ascii", "ignore").decode("ascii")
    # Chuyển thường
    text = text.lower()
    # Thay mọi chuỗi ký tự không phải [a-z0-9] bằng '-'
    text = re.sub(r"[^a-z0-9]+", "-", text)
    # Gộp '---' thành '-'
    text = re.sub(r"-{2,}", "-", text)
    # Bỏ '-' ở đầu/cuối
    text = text.strip("-")
    
    return text or "untitled"


# ============================================================
# TOKEN COUNTING
# ============================================================

_token_counter: Callable[[str], int] | None = None


def _init_token_counter() -> None:
    """Khởi tạo token counter (tiktoken nếu có, fallback = len(text)//4)."""
    global _token_counter
    
    if _token_counter is not None:
        return
    
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        _token_counter = lambda text: len(enc.encode(text))
    except ImportError:
        # Fallback: ~4 ký tự = 1 token
        _token_counter = lambda text: max(1, len(text) // 4)


def count_tokens(text: str) -> int:
    """
    Đếm số token trong text (theo OpenAI's cl100k_base encoding).
    
    Sử dụng tiktoken nếu có sẵn, nếu không dùng heuristic fallback (~4 ký tự/token).
    
    Args:
        text: Chuỗi cần đếm
        
    Returns:
        Số token ước tính
    """
    _init_token_counter()
    return _token_counter(text)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_whitespace(text: str) -> str:
    """
    Chuẩn hóa khoảng trắng: xóa trailing spaces, gộp dòng trống, v.v.
    
    Args:
        text: Chuỗi input
        
    Returns:
        Text sau khi chuẩn hóa
    """
    # Xóa trailing spaces
    text = re.sub(r"[ \t]+\n", "\n", text)
    # Gộp 3 dòng trống hoặc hơn thành 1 dòng trống
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Gộp nhiều space liên tiếp thành 1
    text = re.sub(r"[ \t]{2,}", " ", text)
    
    return text.strip()


def shorten_urls(text: str, max_url_len: int = 80) -> str:
    """
    Giữ nguyên text hiển thị nhưng thay URL dài bằng placeholder để giảm token.
    
    Ví dụ:
        [My Link](https://very-long-url.com/path/to/something)
        -> [My Link](link)  (nếu URL dài hơn max_url_len)
    
    Args:
        text: Markdown text
        max_url_len: Ngưỡng độ dài URL
        
    Returns:
        Text sau khi xử lý
    """
    def replace_url(match):
        link_text = match.group(1)
        url = match.group(2)
        if len(url) > max_url_len:
            return f"[{link_text}](link)"
        return match.group(0)
    
    return re.sub(
        r"\[([^\]]+)\]\((https?://[^\s)]+)\)",
        replace_url,
        text
    )


def replace_images_with_placeholder(html_str: str) -> str:
    """
    Thay mọi thẻ <img> bằng text [Image: tên-file].
    
    Ngăn chặn HTML/base64 image code làm phình to file,
    nhưng vẫn giữ dấu vết (alt text) để biết ảnh là cái gì.
    
    Args:
        html_str: HTML string
        
    Returns:
        HTML với images được thay bằng placeholder
    """
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html_str, "lxml")
    for img in soup.find_all("img"):
        src = img.get("src", "")
        # Lấy phần cuối cùng của URL làm tên file
        filename = src.rsplit("/", 1)[-1].split("?")[0] if src else "unknown"
        # Dùng alt text nếu có, nếu không thì dùng tên file
        alt = img.get("alt", "").strip()
        placeholder = f"[Image: {alt or filename}]"
        # Thay thẻ <img> bằng text
        img.replace_with(placeholder)
    
    return str(soup)
