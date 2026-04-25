import requests
from bs4 import BeautifulSoup
import os
import json
import time
from pathlib import Path
from urllib.parse import urljoin
from typing import List, Dict, Optional

class KASSpider:
    def __init__(self, output_dir: str = "data/raw/kas"):
        self.base_url = "https://kas.or.id"
        self.output_path = Path(output_dir).absolute()
        self.output_path.mkdir(parents=True, exist_ok=True)
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
        
        content_div = soup.find('div', class_='entry-content')
        if not content_div:
            return None

        return {
            "title": title,
            "url": article_url,
            "content": content_div.get_text(separator="\n", strip=True),
            "source": "kas.or.id"
        }

    def crawl_all(self, categories: List[str], max_pages: int = 5):
        all_data = []
        output_file = self.output_path / "kas_articles.jsonl"
        print(f"[*] Crawling {len(categories)} categories. Output: {output_file}")

        for category_url in categories:
            current_page = 1
            while current_page <= max_pages:
                page_url = category_url if current_page == 1 else urljoin(category_url, f"page/{current_page}/")
                print(f"  [*] Page {current_page}: {page_url}")
                
                soup = self.get_soup(page_url)
                if not soup: break

                articles = soup.find_all(['h1', 'h2', 'h3'], class_=re.compile(r'title|entry'))
                if not articles: break

                for art in articles:
                    link_tag = art.find('a', href=True)
                    if link_tag:
                        art_url = link_tag['href']
                        if "/category/" in art_url: continue
                        
                        data = self.extract_article(art_url)
                        if data:
                            all_data.append(data)
                            print(f"    [OK] {data['title']}")
                        time.sleep(0.5)

                next_page = soup.find('a', string=re.compile(r'Next|Berikutnya|>', re.I))
                if not next_page: break
                current_page += 1

        print(f"[*] Crawl finished. Saving {len(all_data)} articles...")
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in all_data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"[*] File saved: {output_file.exists()}")

if __name__ == "__main__":
    import re
    spider = KASSpider()
    cats = [
        "https://kas.or.id/category/dokumen-gereja/",
        "https://kas.or.id/category/surat-gembala/"
    ]
    spider.crawl_all(cats, max_pages=10)
