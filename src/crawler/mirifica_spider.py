import requests
from bs4 import BeautifulSoup
import os
import json
import time
from pathlib import Path
from urllib.parse import urljoin
from typing import List, Dict, Optional

class MirificaSpider:
    def __init__(self, output_dir: str = "data/raw/mirifica"):
        self.base_url = "https://mirifica.net"
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
        
        content_div = soup.find('div', class_='td-post-content')
        if not content_div:
            return None

        # Extract text and handle potential PDF links
        pdf_links = []
        for a in content_div.find_all('a', href=True):
            if a['href'].lower().endswith('.pdf'):
                pdf_links.append(urljoin(article_url, a['href']))

        return {
            "title": title,
            "url": article_url,
            "content": content_div.get_text(separator="\n", strip=True),
            "pdf_links": pdf_links,
            "source": "mirifica.net"
        }

    def crawl_category(self, category_url: str, max_pages: int = 5):
        current_page = 1
        output_file = self.output_dir / "mirifica_articles.jsonl"

        while current_page <= max_pages:
            page_url = category_url if current_page == 1 else urljoin(category_url, f"page/{current_page}/")
            print(f"[*] Crawling {page_url}")
            
            soup = self.get_soup(page_url)
            if not soup:
                break

            articles = soup.find_all('h3', class_='entry-title')
            if not articles:
                break

            for art in articles:
                link_tag = art.find('a', href=True)
                if link_tag:
                    art_url = link_tag['href']
                    print(f"  [+] Extracting: {art_url}")
                    data = self.extract_article(art_url)
                    if data:
                        with open(output_file, 'a', encoding='utf-8') as f:
                            f.write(json.dumps(data, ensure_ascii=False) + "\n")
                    time.sleep(1)

            next_page = soup.find('a', class_='next page-numbers')
            if not next_page:
                break
            current_page += 1

if __name__ == "__main__":
    spider = MirificaSpider()
    categories = [
        "https://mirifica.net/category/dokpen/"
    ]
    for cat in categories:
        spider.crawl_category(cat, max_pages=10)
