import requests
from bs4 import BeautifulSoup
import os
import json
import time
import re
from pathlib import Path
from urllib.parse import urljoin
from typing import List, Dict, Optional

class HidupSpider:
    def __init__(self, output_dir: str = "data/raw/hidup"):
        self.base_url = "https://www.hidupkatolik.com"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        try:
            response = requests.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"[!] Error fetching {url}: {e}")
            return None

    def extract_article(self, article_url: str) -> Optional[Dict]:
        soup = self.get_soup(article_url)
        if not soup:
            return None

        title = soup.find('h1', class_='jeg_post_title')
        if not title:
            title = soup.find('h1', class_='entry-title')
        if not title:
            title = soup.select_one('.tdb-title-text')
            
        title = title.get_text(strip=True) if title else "No Title"
        
        # Newspaper theme content selector
        content_div = soup.find('div', class_='td-post-content')
        if not content_div:
            content_div = soup.select_one('.tdb-block-inner.tdb-single-content')
        if not content_div:
            content_div = soup.find('div', class_='jeg_post_content')
        if not content_div:
            content_div = soup.find('div', class_='entry-content')
            
        if not content_div:
            return None

        return {
            "title": title,
            "url": article_url,
            "content": content_div.get_text(separator="\n", strip=True),
            "source": "hidupkatolik.com"
        }

    def crawl_category(self, category_url: str, max_pages: int = 5):
        current_page = 1
        # Use category name in filename
        cat_name = category_url.strip('/').split('/')[-1]
        output_file = self.output_dir / f"hidup_{cat_name}.jsonl"

        while current_page <= max_pages:
            page_url = category_url if current_page == 1 else urljoin(category_url, f"page/{current_page}/")
            print(f"[*] Crawling {page_url}")
            
            soup = self.get_soup(page_url)
            if not soup:
                break

            # Newspaper theme selectors
            articles = soup.select('.td-module-title a')
            if not articles:
                articles = soup.select('.jeg_post_title a')
            
            if not articles:
                print("    [-] No articles found on this page.")
                break

            found_on_page = 0
            seen_urls = set()
            for link_tag in articles:
                art_url = link_tag.get('href')
                if not art_url or art_url in seen_urls or "/category/" in art_url:
                    continue
                
                seen_urls.add(art_url)
                print(f"  [+] Extracting: {art_url}")
                data = self.extract_article(art_url)
                if data:
                    with open(output_file, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(data, ensure_ascii=False) + "\n")
                    found_on_page += 1
                time.sleep(1)

            if found_on_page == 0:
                print("    [-] Found no unique articles on this page.")
                break

            # Next page check
            next_page = soup.select_one('.page-nav a i.td-icon-menu-right')
            if not next_page:
                next_page = soup.select_one('.page-numbers.next')
            
            if not next_page:
                break
            current_page += 1

if __name__ == "__main__":
    spider = HidupSpider()
    categories = [
        "https://www.hidupkatolik.com/category/kekatolikan/",
        "https://www.hidupkatolik.com/category/katekese/",
        "https://www.hidupkatolik.com/category/konsultasi-iman/"
    ]
    for cat in categories:
        # Just 2 pages for testing as requested to "help scrape"
        spider.crawl_category(cat, max_pages=2)
