"""
Pipeline chính: điều phối toàn bộ quá trình xử lý từ JSON -> docs + chunks.
"""

import json
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple
from bs4 import BeautifulSoup

from . import config
from .utils import slugify, count_tokens
from .html_cleaner import (
    clean_and_prepare_html,
    build_id_to_slug_map,
)
from .markdown_converter import (
    html_to_markdown,
    normalize_markdown,
)
from .chunking import chunk_markdown
from .audit import run_audit


def load_articles(path: Path | str) -> List[Dict]:
    """
    Load danh sách article từ JSON file.
    
    Args:
        path: Đường dẫn file JSON
        
    Returns:
        List article dict
        
    Raises:
        FileNotFoundError: File không tồn tại
        json.JSONDecodeError: JSON không hợp lệ
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def filter_empty_articles(articles: List[Dict], min_len: int) -> Tuple[List[Dict], int]:
    """
    Lọc bỏ article rỗng / quá ngắn.
    
    Dùng plain text (không tính HTML tag) để đo độ dài.
    
    Args:
        articles: Danh sách articles
        min_len: Ngưỡng độ dài tối thiểu (ký tự plain text)
        
    Returns:
        (filtered_articles, skipped_count)
    """
    filtered = []
    skipped = 0
    
    for a in articles:
        raw = a.get("body") or ""
        # Parse HTML, lấy plain text
        plain = BeautifulSoup(raw, "lxml").get_text(" ", strip=True)
        
        if len(plain) >= min_len:
            filtered.append(a)
        else:
            skipped += 1
    
    return filtered, skipped


def dedup_articles_by_title(articles: List[Dict]) -> Tuple[List[Dict], int]:
    """
    Loại bỏ articles trùng title (giữ bản updated_at mới nhất).
    
    Args:
        articles: Danh sách articles
        
    Returns:
        (dedup_articles, dedup_count)
    """
    by_title = {}
    
    for a in articles:
        title = a["title"].strip().lower()
        if title not in by_title or a["updated_at"] > by_title[title]["updated_at"]:
            by_title[title] = a
    
    dedup_articles = list(by_title.values())
    dedup_count = len(articles) - len(dedup_articles)
    
    return dedup_articles, dedup_count


def build_front_matter(article: Dict, slug: str) -> str:
    """
    Tạo YAML front-matter cho markdown file.
    
    Format:
        ---
        title: "..."
        source_url: "..."
        article_id: 123
        ...
        ---
    
    Args:
        article: Article dict
        slug: Filename slug
        
    Returns:
        Front-matter string (bao gồm ---)
    """
    # Escape dấu ngoặc kép trong title
    title = article["title"].replace('"', "'")
    
    lines = [
        "---",
        f'title: "{title}"',
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


def process_article(
    article: Dict,
    id_to_slug: Dict[int, str],
    docs_dir: Path,
    seen_slugs: Counter
) -> Tuple[str, List[Dict]]:
    """
    Xử lý 1 article: clean HTML, convert to Markdown, chunk, ghi file.
    
    Args:
        article: Article dict
        id_to_slug: Mapping article_id -> slug
        docs_dir: Output directory cho markdown files
        seen_slugs: Counter để tránh collision slug
        
    Returns:
        (output_filename, chunks_list)
        
    Raises:
        Không raise exception, xử lý gracefully nếu có lỗi
    """
    try:
        # Bước 1-3: Clean HTML, Rewrite internal links, Replace images with placeholders in one pass
        raw_html = article.get("body") or ""
        cleaned_html = clean_and_prepare_html(raw_html, id_to_slug)
        markdown_body = html_to_markdown(cleaned_html)
        
        # Bước 5: Normalize Markdown (xóa boilerplate, v.v.)
        markdown_body = normalize_markdown(markdown_body)
        
        # Bước 6: Tạo filename slug
        slug = id_to_slug[article["id"]]
        seen_slugs[slug] += 1
        
        # Tránh slug collision
        if seen_slugs[slug] > 1:
            slug = slug.replace(".md", f"-{article['id']}.md")
        
        # Bước 7: Build full markdown (front-matter + title + body)
        front_matter = build_front_matter(article, slug)
        full_md = front_matter + f"# {article['title']}\n\n" + markdown_body
        
        # Bước 8: Write markdown file
        out_path = docs_dir / slug
        out_path.write_text(full_md, encoding="utf-8")
        
        # Bước 9: Chunk cho vector DB
        chunks = chunk_markdown(markdown_body, article["title"])
        
        # Enrich chunks với metadata
        chunks_with_meta = []
        for i, c in enumerate(chunks):
            # "text": nội dung raw của chunk (dùng cho audit + hiển thị preview,
            #   giữ nguyên để các rule audit dựa trên cấu trúc markdown thô
            #   (starts_mid_sentence, broken_code_block, v.v.) không bị lệch).
            # "embedding_text": text thực sự nên đưa vào lúc embed lên Vector DB -
            #   có prefix "Article Title — Section Heading" để mô hình embedding
            #   "thấy" được ngữ cảnh của chunk, thay vì chunk trơ trọi không biết
            #   đang nói về chủ đề gì (quan trọng khi chunk không tự lặp lại từ khóa
            #   chính, ví dụ đoạn step 3/4 của 1 hướng dẫn).
            heading = c["heading"].strip()
            title = article["title"].strip()
            if heading and heading.lower() != title.lower():
                context_header = f"{title} — {heading}"
            else:
                context_header = title
            embedding_text = f"{context_header}\n\n{c['text']}"

            chunks_with_meta.append({
                "chunk_id": f"{article['id']}-{i}",
                "article_id": article["id"],
                "article_title": article["title"],
                "heading": c["heading"],
                "source_url": article["html_url"],
                "section_id": article.get("section_id"),
                "updated_at": article.get("updated_at"),
                "labels": article.get("label_names") or [],
                "text": c["text"],
                "embedding_text": embedding_text,
                "token_count": count_tokens(c["text"]),
                "embedding_token_count": count_tokens(embedding_text),
            })
        
        return slug, chunks_with_meta
        
    except Exception as e:
        print(f"  Warning: Error processing article {article.get('id')}: {e}")
        return None, []


def run_pipeline(
    input_json: Path | str = config.INPUT_JSON_PATH,
    output_docs: Path | str = config.OUTPUT_DOCS_PATH,
    output_chunks: Path | str = config.OUTPUT_CHUNKS_PATH,
    output_audit: Path | str = config.OUTPUT_AUDIT_PATH,
    verbose: bool = True,
) -> Dict:
    """
    Chạy toàn bộ pipeline: load, process, chunk, audit.
    
    Args:
        input_json: Đường dẫn file input JSON
        output_docs: Đường dẫn output directory cho markdown
        output_chunks: Đường dẫn output file chunks.jsonl
        output_audit: Đường dẫn output file audit_report.jsonl
        verbose: Print detailed progress
        
    Returns:
        Dict thống kê pipeline:
            {
                "total_articles": int,
                "skipped_empty": int,
                "dedup_count": int,
                "processed_articles": int,
                "total_chunks": int,
                "avg_chunks_per_article": float,
                "output_docs": str,
                "output_chunks": str,
                "output_audit": str,
                "audit_stats": dict,
            }
    
    Raises:
        FileNotFoundError: Input file không tồn tại
        json.JSONDecodeError: Input JSON không hợp lệ
    """
    # Chuẩn hóa paths
    input_json = Path(input_json)
    output_docs = Path(output_docs)
    output_chunks = Path(output_chunks)
    output_audit = Path(output_audit)
    
    # Tạo output directories
    output_docs.mkdir(parents=True, exist_ok=True)
    
    if verbose:
        print("\n" + "=" * 60)
        print("OptiSigns RAG Pipeline")
        print("=" * 60)
    
    # ========== BƯỚC 1: LOAD ==========
    if verbose:
        print(f"\n[1] Loading articles from {input_json}...")
    
    articles = load_articles(input_json)
    
    if verbose:
        print(f"    Total: {len(articles)} articles")
    
    # ========== BƯỚC 2: FILTER EMPTY ==========
    if verbose:
        print(f"\n[2] Filtering empty articles (min {config.MIN_BODY_TEXT_LEN} chars)...")
    
    filtered, skipped_empty = filter_empty_articles(
        articles,
        config.MIN_BODY_TEXT_LEN
    )
    
    if verbose:
        print(f"    Skipped: {skipped_empty}")
        print(f"    Remaining: {len(filtered)}")
    
    # ========== BƯỚC 3: DEDUP ==========
    if verbose:
        print(f"\n[3] Dedup by title (keeping newest by updated_at)...")
    
    dedup_articles, dedup_count = dedup_articles_by_title(filtered)
    
    if verbose:
        print(f"    Dedup count: {dedup_count}")
        print(f"    Final: {len(dedup_articles)}")
    
    # ========== BƯỚC 4: BUILD ID -> SLUG MAP ==========
    if verbose:
        print(f"\n[4] Building ID->Slug mapping...")
    
    id_to_slug = build_id_to_slug_map(dedup_articles)
    
    # ========== BƯỚC 5: PROCESS ARTICLES ==========
    if verbose:
        print(f"\n[5] Processing {len(dedup_articles)} articles...")
    
    all_chunks = []
    seen_slugs: Counter = Counter()
    processed_count = 0
    
    for idx, article in enumerate(dedup_articles, 1):
        if verbose:
            print(f"    [{idx}/{len(dedup_articles)}] {article['title'][:50]}...")
        
        slug, chunks = process_article(
            article,
            id_to_slug,
            output_docs,
            seen_slugs
        )
        
        if slug:
            processed_count += 1
            all_chunks.extend(chunks)
    
    if verbose:
        print(f"    Processed: {processed_count}")
        print(f"    Total chunks: {len(all_chunks)}")
    
    # ========== BƯỚC 6: WRITE CHUNKS ==========
    if verbose:
        print(f"\n[6] Writing chunks to {output_chunks}...")
    
    with open(output_chunks, "w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    
    if verbose:
        print(f"    Done: {len(all_chunks)} chunks")
    
    # ========== BƯỚC 7: AUDIT ==========
    if verbose:
        print(f"\n[7] Running audit...")
    
    audit_stats = run_audit(all_chunks, output_audit)
    
    # ========== SUMMARY ==========
    avg_chunks = len(all_chunks) / len(dedup_articles) if dedup_articles else 0
    
    if verbose:
        print("\n" + "=" * 60)
        print("PIPELINE COMPLETE")
        print("=" * 60)
        print(f"Output markdown: {output_docs}/ ({processed_count} files)")
        print(f"Output chunks:   {output_chunks} ({len(all_chunks)} lines)")
        print(f"Output audit:    {output_audit}")
        print(f"Avg chunks/article: {avg_chunks:.1f}")
        print("=" * 60 + "\n")
    
    return {
        "total_articles": len(articles),
        "skipped_empty": skipped_empty,
        "dedup_count": dedup_count,
        "processed_articles": processed_count,
        "total_chunks": len(all_chunks),
        "avg_chunks_per_article": avg_chunks,
        "output_docs": str(output_docs),
        "output_chunks": str(output_chunks),
        "output_audit": str(output_audit),
        "audit_stats": audit_stats,
    }