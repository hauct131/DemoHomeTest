import requests
import time
import json

BASE = "https://support.optisigns.com/api/v2/help_center/en-us"

def get_all(endpoint):
    """Lấy toàn bộ dữ liệu có phân trang từ 1 endpoint Zendesk"""
    results = []
    url = f"{BASE}/{endpoint}.json?per_page=100"
    while url:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        key = endpoint  # vd: "articles", "categories", "sections"
        results.extend(data[key])
        url = data.get("next_page")  # Zendesk tự trả link trang kế tiếp
        time.sleep(0.3)  # lịch sự với server
    return results

# 1. Lấy toàn bộ category
categories = get_all("categories")

# 2. Lấy toàn bộ section
sections = get_all("sections")

# 3. Lấy toàn bộ bài viết (kèm nội dung HTML đầy đủ trong field "body")
articles = get_all("articles")

print(f"{len(categories)} categories, {len(sections)} sections, {len(articles)} articles")

# Lưu ra file
with open("optisigns_articles.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)