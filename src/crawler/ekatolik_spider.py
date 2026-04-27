import requests
from bs4 import BeautifulSoup
import os
import json
import time
from pathlib import Path
from urllib.parse import urljoin
from typing import List, Dict, Optional

class EKatolikSpider:
    def __init__(self, output_dir: str = "data/raw/ekatolik"):
        self.base_url = "https://ekatolik.com"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def extract_prayer(self, url: str) -> Optional[Dict]:
        try:
            r = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            # EKatolik often puts prayer title in <h1>
            title = soup.find('h1')
            title = title.get_text(strip=True) if title else "No Title"
            
            # The prayer content is usually the largest text block or specific div
            # Based on standard Next.js / React patterns often seen on such sites
            content_div = soup.find('article') or soup.find('main')
            
            if not content_div:
                return None

            return {
                "title": title,
                "url": url,
                "content": content_div.get_text(separator="\n", strip=True),
                "source": "ekatolik.com"
            }
        except: return None

    def crawl_homepage(self):
        output_file = self.output_dir / "ekatolik_prayers.jsonl"
        print(f"[*] Scanning homepage for prayer links...")
        
        try:
            r = requests.get(self.base_url, headers=self.headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            # Collect all /p/ links (Prayer posts)
            links = [urljoin(self.base_url, a['href']) for a in soup.find_all('a', href=True) if '/p/' in a['href']]
            links = list(set(links))
            
            print(f"[*] Found {len(links)} unique prayers to extract.")
            
            count = 0
            for link in links:
                data = self.extract_prayer(link)
                if data:
                    with open(output_file, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(data, ensure_ascii=False) + "\n")
                    count += 1
                    print(f"    [OK] {data['title'][:50]}...")
                time.sleep(1)
            
            print(f"[*] Done! Captured {count} prayers.")
        except Exception as e:
            print(f"[!] Error: {e}")

if __name__ == "__main__":
    spider = EKatolikSpider()
    # Clear file if exists
    out = Path("data/raw/ekatolik/ekatolik_prayers.jsonl")
    if out.exists(): out.unlink()
    spider.crawl_homepage()
