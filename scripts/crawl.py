import sys
from pathlib import Path

# Thêm project root vào sys.path để import src/
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src import config
import requests
import time
import json

BASE = "https://support.optisigns.com/api/v2/help_center/en-us"


def get_all(endpoint):
    """Lấy toàn bộ dữ liệu có phân trang từ 1 endpoint Zendesk"""
    results = []
    url = f"{BASE}/{endpoint}.json?per_page=100"
    while url:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        r.raise_for_status()
        data = r.json()
        key = endpoint  # vd: "articles", "categories", "sections"
        results.extend(data[key])
        url = data.get("next_page")  # Zendesk tự trả link trang kế tiếp
        time.sleep(0.3)  # lịch sự với server
    return results


def run_crawl(verbose: bool = True) -> dict:
    """
    Re-scrape toàn bộ categories/sections/articles từ Zendesk Help Center
    và ghi đè lên config.INPUT_JSON_PATH.

    Đây là bước "Re-scrape" chạy đầu tiên trong daily job, TRƯỚC khi
    run_pipeline() xử lý delta (hash/updated_at) cho phần chunk + upload.

    Returns:
        Dict thống kê: {categories, sections, articles}
    """
    if verbose:
        print("\n" + "=" * 60)
        print("STEP 0: Re-scraping Zendesk Help Center")
        print("=" * 60)

    categories = get_all("categories")
    sections = get_all("sections")
    articles = get_all("articles")

    if verbose:
        print(f"    Categories: {len(categories)}")
        print(f"    Sections:   {len(sections)}")
        print(f"    Articles:   {len(articles)}")

    config.INPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(config.INPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    if verbose:
        print(f"    Saved -> {config.INPUT_JSON_PATH}")

    return {
        "categories": len(categories),
        "sections": len(sections),
        "articles": len(articles),
    }


if __name__ == "__main__":
    stats = run_crawl()
    print(f"\n{stats['categories']} categories, {stats['sections']} sections, {stats['articles']} articles")