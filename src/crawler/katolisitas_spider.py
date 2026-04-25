import requests
from bs4 import BeautifulSoup
import os
import json
import time
import re
from pathlib import Path
from urllib.parse import urljoin
from typing import List, Dict, Optional

class KatolisitasSpider:
    def __init__(self, output_dir: str = "data/raw/katolisitas"):
        self.base_url = "https://www.katolisitas.org"
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

        title = soup.find('h1', class_='entry-title')
        title = title.get_text(strip=True) if title else "No Title"
        
        # Newspaper theme content selector
        content_div = soup.find('div', class_='td-post-content')
        if not content_div:
            # Fallback for older posts
            content_div = soup.find('div', class_='entry-content')
            
        if not content_div:
            return None

        return {
            "title": title,
            "url": article_url,
            "content": content_div.get_text(separator="\n", strip=True),
            "source": "katolisitas.org"
        }

    def crawl_category(self, category_url: str, max_pages: int = 5):
        current_page = 1
        output_file = self.output_dir / "katolisitas_articles.jsonl"

        while current_page <= max_pages:
            page_url = category_url if current_page == 1 else urljoin(category_url, f"page/{current_page}/")
            print(f"[*] Crawling {page_url}")
            
            soup = self.get_soup(page_url)
            if not soup:
                break

            # Katolisitas (Newspaper theme) uses h3 for modules in archives
            articles = soup.find_all('h3', class_='entry-title')
            if not articles:
                articles = soup.find_all(['h1', 'h2', 'h3'], class_=re.compile(r'title|entry'))
            
            if not articles:
                print("    [-] No articles found on this page.")
                break

            found_on_page = 0
            for art in articles:
                link_tag = art.find('a', href=True)
                if link_tag:
                    art_url = link_tag['href']
                    # Skip if it's just a category link or main page
                    if "/category/" in art_url: continue
                    
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
            next_page = soup.find('a', class_='next page-numbers')
            if not next_page:
                # Try generic "Next" or "Berikutnya"
                next_page = soup.find('a', string=re.compile(r'Next|Berikutnya|>', re.I))
            
            if not next_page:
                break
            current_page += 1

if __name__ == "__main__":
    spider = KatolisitasSpider()
    categories = [
        "https://www.katolisitas.org/category/dokumen-gereja/",
        "https://www.katolisitas.org/category/katekese/katekese-dewasa/"
    ]
    for cat in categories:
        spider.crawl_category(cat, max_pages=10)
