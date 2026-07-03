"""
Các hàm liên quan đến làm sạch HTML:
- strip_unwanted_tags
- strip_internal_toc
- strip_anchor_targets
- clean_html
- rewrite_internal_links
"""

import re
from typing import Dict
from bs4 import BeautifulSoup

from . import config

def clean_and_prepare_html(raw_html: str, id_to_slug: Dict[int, str]) -> str:
    """
    Thực hiện làm sạch HTML, rewrite links và xử lý ảnh trên MỘT thực thể soup duy nhất.
    """
    soup = BeautifulSoup(raw_html or "", "lxml")
    
    # 1. Strip unwanted tags
    for tag_name in config.TAGS_TO_STRIP:
        for tag in soup.find_all(tag_name):
            tag.decompose()
            
    # 2. Strip internal TOC
    body_root = soup.body if soup.body else soup
    first_elements = body_root.find_all(recursive=False)
    if first_elements:
        first = first_elements[0]
        if first.name == "ul":
            links = first.find_all("a", href=True)
            if links and all(a["href"].startswith("#") for a in links):
                first.decompose()
                
    # 3. Strip anchor targets
    for a in soup.find_all("a", attrs={"name": True}):
        if not a.get_text(strip=True):
            a.decompose()
            
    # 4. Rewrite internal links
    for a_tag in soup.find_all("a", href=True):
        match = re.search(r"/articles/(\d+)(-[^/#]*)?(?:#.*)?$", a_tag["href"])
        if match:
            article_id = int(match.group(1))
            if article_id in id_to_slug:
                a_tag["href"] = id_to_slug[article_id]
                
    # 5. Replace images with placeholders
    for img in soup.find_all("img"):
        src = img.get("src", "")
        filename = src.rsplit("/", 1)[-1].split("?")[0] if src else "unknown"
        alt = img.get("alt", "").strip()
        img.replace_with(f"[Image: {alt or filename}]")
        
    return str(soup)



def strip_unwanted_tags(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Loại bỏ các thẻ HTML không cần thiết (script, style, iframe, v.v.).
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        BeautifulSoup object sau khi xóa thẻ
    """
    for tag_name in config.TAGS_TO_STRIP:
        for tag in soup.find_all(tag_name):
            tag.decompose()
    return soup


def strip_internal_toc(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Xóa <ul> đầu bài nếu TOÀN BỘ <a> bên trong trỏ tới anchor nội bộ (#...).
    
    Đây là Table of Contents (TOC) tự động, không cần thiết cho embedding.
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        BeautifulSoup object sau khi xóa TOC (nếu có)
    """
    body_root = soup.body if soup.body else soup
    first_elements = body_root.find_all(recursive=False)
    
    if not first_elements:
        return soup
    
    first = first_elements[0]
    if first.name == "ul":
        links = first.find_all("a", href=True)
        # Nếu tất cả link đều trỏ tới anchor nội bộ -> đây là TOC
        if links and all(a["href"].startswith("#") for a in links):
            first.decompose()
    
    return soup


def strip_anchor_targets(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Xóa các <a name="..."></a> rỗng dùng làm điểm neo cho TOC đã xóa.
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        BeautifulSoup object sau khi xóa anchor targets
    """
    for a in soup.find_all("a", attrs={"name": True}):
        if not a.get_text(strip=True):
            a.decompose()
    return soup


def clean_html(raw_html: str) -> str:
    """
    Làm sạch HTML: xóa script, style, TOC, anchor targets, v.v.
    
    Pipeline:
        1. Parse HTML
        2. Xóa unwanted tags
        3. Xóa internal TOC
        4. Xóa anchor targets
        
    Args:
        raw_html: HTML string (có thể là None/rỗng)
        
    Returns:
        Cleaned HTML string
        
    Raises:
        Không raise exception, luôn trả về string (có thể rỗng)
    """
    soup = BeautifulSoup(raw_html or "", "lxml")
    soup = strip_unwanted_tags(soup)
    soup = strip_internal_toc(soup)
    soup = strip_anchor_targets(soup)
    return str(soup)


def build_id_to_slug_map(articles: list[dict]) -> Dict[int, str]:
    """
    Xây dựng mapping article_id -> slug (tên file).
    
    Dùng để rewrite internal links trong HTML (từ /articles/{id} 
    thành {slug}.md).
    
    Args:
        articles: Danh sách article dict
        
    Returns:
        {article_id: "title-slug.md", ...}
    """
    from .utils import slugify
    
    mapping = {}
    for a in articles:
        slug = slugify(a["title"]) + ".md"
        mapping[a["id"]] = slug
    return mapping


def rewrite_internal_links(clean_html_str: str, id_to_slug: Dict[int, str]) -> str:
    """
    Rewrite internal links từ Zendesk URL format (/articles/{id})
    thành local file references ({slug}.md).
    
    Ví dụ:
        /articles/123456-my-article#section
        -> my-article.md
    
    Args:
        clean_html_str: HTML string
        id_to_slug: Mapping từ article_id sang slug
        
    Returns:
        HTML string với links được rewrite
    """
    soup = BeautifulSoup(clean_html_str, "lxml")
    
    for a_tag in soup.find_all("a", href=True):
        # Match pattern: /articles/{id}-{slug}#{anchor}
        match = re.search(r"/articles/(\d+)(-[^/#]*)?(?:#.*)?$", a_tag["href"])
        if match:
            article_id = int(match.group(1))
            if article_id in id_to_slug:
                a_tag["href"] = id_to_slug[article_id]
    
    return str(soup)
