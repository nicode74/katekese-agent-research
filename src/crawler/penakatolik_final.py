import requests
from bs4 import BeautifulSoup
import os
import json
import time
from pathlib import Path
from urllib.parse import urljoin

class PenaKatolikFinal:
    def __init__(self):
        self.base_url = "https://penakatolik.com"
        # Use a very explicit absolute path
        self.output_file = Path(r"D:\pena_test.jsonl")
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    def extract(self, url):
        try:
            r = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('h1', class_='entry-title')
            content = soup.find('div', class_='entry-content')
            if title and content:
                return {
                    "title": title.get_text(strip=True),
                    "content": content.get_text(separator="\n", strip=True),
                    "url": url,
                    "source": "penakatolik.com"
                }
        except: return None
        return None

    def crawl(self, category_url, max_pages=3):
        print(f"[*] Starting {category_url}")
        for page in range(1, max_pages + 1):
            url = category_url if page == 1 else f"{category_url}page/{page}/"
            print(f"  [Page {page}] Fetching...")
            try:
                r = requests.get(url, headers=self.headers, timeout=15)
                soup = BeautifulSoup(r.text, 'html.parser')
                links = [a['href'] for a in soup.find_all('a', rel='bookmark') if 'href' in a.attrs]
                
                # Deduplicate
                links = list(set(links))
                print(f"    Found {len(links)} links.")
                
                for link in links:
                    data = self.extract(link)
                    if data:
                        # Write and Flush immediately
                        with open(self.output_file, 'a', encoding='utf-8') as f:
                            f.write(json.dumps(data, ensure_ascii=False) + "\n")
                            f.flush()
                        print(f"      [SAVED] {data['title'][:50]}...")
                    time.sleep(0.5)
            except Exception as e:
                print(f"    [!] Error on page {page}: {e}")
                break

if __name__ == "__main__":
    p = PenaKatolikFinal()
    # Clear file if exists
    if p.output_file.exists(): p.output_file.unlink()
    
    cats = [
        "https://penakatolik.com/category/pengetahuan-iman/",
        "https://penakatolik.com/category/doa-doa-katolik/"
    ]
    for c in cats:
        p.crawl(c, max_pages=5)
    print(f"[*] Finished. File exists: {p.output_file.exists()}, Size: {p.output_file.stat().st_size if p.output_file.exists() else 0}")
