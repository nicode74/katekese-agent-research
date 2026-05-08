import requests
from bs4 import BeautifulSoup
import json
import time
import os
from pathlib import Path
from urllib.parse import urljoin
from typing import List, Dict, Optional

class PapalSpider:
    def __init__(self, output_dir: str = "data/raw/papal_encyclicals"):
        self.base_url = "https://www.papalencyclicals.net/"
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

    def get_all_pope_links(self) -> List[str]:
        """Gets links to individual Pope directories from the pope-directory page."""
        print("[*] Fetching Pope Directory...")
        soup = self.get_soup(urljoin(self.base_url, "pope-directory"))
        if not soup:
            return []
        
        links = []
        # Try finding links in UberMenu
        for a in soup.find_all('a', class_='ubermenu-target', href=True):
            links.append(a['href'])
        
        # Try finding in Select options
        for option in soup.find_all('option'):
            val = option.get('value')
            if val and self.base_url in val:
                links.append(val)
        
        # Clean and prioritize category links
        final_links = []
        for l in set(links):
            if "/category/" in l or any(p in l for p in ["/franc", "/ben16", "/jp02", "/leo13"]):
                final_links.append(l)
        
        return list(set(final_links))

    def extract_document(self, doc_url: str) -> Optional[Dict]:
        """Extracts title, date, and content from a document page."""
        soup = self.get_soup(doc_url)
        if not soup:
            return None

        title_tag = soup.find('h1', class_='entry-title')
        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        
        content_div = soup.find('div', class_='entry-content')
        if not content_div:
            return None

        content = content_div.get_text(separator="\n", strip=True)
        # Check if it's too short (likely just a list of links or a stub)
        if len(content) < 500:
            print(f"      [SKIP] Content too short ({len(content)} chars)")
            return None

        return {
            "title": title,
            "url": doc_url,
            "content": content,
            "language": "en"
        }

    def crawl_pope(self, pope_url: str, limit: int = 5):
        """Crawls documents for a specific Pope."""
        print(f"[*] Crawling Pope Page: {pope_url}")
        soup = self.get_soup(pope_url)
        if not soup:
            return

        all_links = []
        content = soup.find('div', class_='entry-content') or soup
            
        # Get the "pope slug" from the URL to filter out the pope's own landing page
        pope_slug = pope_url.rstrip('/').split('/')[-1]

        for a in content.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(self.base_url, href).rstrip('/')
            
            # Filter criteria:
            if self.base_url in full_url:
                # 1. Skip non-content pages
                if any(x in full_url for x in ["/category/", "/tag/", "/pope-directory", "/about", "/contact", "/document-directory", "/popelist"]):
                    continue
                # 2. Skip top-level pope pages (the slug itself)
                url_slug = full_url.split('/')[-1]
                if url_slug == pope_slug:
                    continue
                # 3. Skip formats like .epub, .mobi, .pdf (unless we want to download them)
                if any(full_url.endswith(ext) for ext in [".epub", ".mobi", ".pdf"]):
                    continue
                
                all_links.append(full_url)
        
        doc_links = list(set(all_links))
        print(f"  [+] Found {len(doc_links)} internal potential document links. Crawling up to {limit}.")
        
        output_file = self.output_dir / "papal_docs.jsonl"
        count = 0
        for link in doc_links:
            if count >= limit:
                break
            
            print(f"    [+] Extracting: {link}")
            data = self.extract_document(link)
            if data:
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")
                count += 1
            time.sleep(1)

    def run_full_crawl(self, pope_limit: int = 3, docs_per_pope: int = 5):
        pope_links = self.get_all_pope_links()
        print(f"[*] Found {len(pope_links)} potential Pope links.")
        
        # Sort to get some predictable ones for testing
        pope_links.sort()
        
        count = 0
        for p_url in pope_links:
            if count >= pope_limit:
                break
            # Skip some generic list pages
            if any(x in p_url for x in ["popelist", "pope-directory", "document-directory"]):
                continue
                
            self.crawl_pope(p_url, limit=docs_per_pope)
            count += 1

if __name__ == "__main__":
    spider = PapalSpider()
    # Full crawl: All popes, up to 100 docs each
    spider.run_full_crawl(pope_limit=100, docs_per_pope=100)
