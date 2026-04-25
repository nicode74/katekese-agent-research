import requests
from bs4 import BeautifulSoup
import os
import json
import time
from pathlib import Path
from urllib.parse import urljoin
from typing import List, Dict, Optional

class KWISpider:
    def __init__(self, base_url: str = "https://dokpenkwi.org", output_dir: str = "data/raw/kwi"):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.pdf_dir = self.output_dir / "pdfs"
        
        # Create folders
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Helper to get BeautifulSoup object from URL."""
        try:
            response = requests.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"[!] Error fetching {url}: {e}")
            return None

    def extract_article_data(self, article_url: str) -> Optional[Dict]:
        """Extract title, content, and pdf links from an article page."""
        soup = self.get_soup(article_url)
        if not soup:
            return None

        title = soup.find('h1', class_='entry-title')
        title = title.get_text(strip=True) if title else "No Title"
        
        # Main content selector for Newspaper theme
        content_div = soup.find('div', class_='td-post-content')
        if not content_div:
            return None

        # Extract PDF links inside content
        pdf_links = []
        for a in content_div.find_all('a', href=True):
            if a['href'].lower().endswith('.pdf'):
                pdf_links.append(urljoin(article_url, a['href']))

        return {
            "title": title,
            "url": article_url,
            "content": content_div.get_text(separator="\n", strip=True),
            "pdf_links": pdf_links,
            "category": "Dokumen Gereja" # Default, can be improved
        }

    def crawl_category(self, category_url: str, max_pages: int = 5):
        """Crawl all articles in a category with pagination."""
        current_page = 1
        all_data = []
        output_file = self.output_dir / "kwi_articles.jsonl"

        while current_page <= max_pages:
            page_url = category_url if current_page == 1 else urljoin(category_url, f"page/{current_page}/")
            print(f"[*] Crawling Page {current_page}: {page_url}")
            
            soup = self.get_soup(page_url)
            if not soup:
                break

            # Find all article links on the page
            # Based on Newspaper theme structure
            articles = soup.find_all('h3', class_='entry-title')
            if not articles:
                # Try another common theme structure if Newspaper doesn't match exactly
                articles = soup.find_all('h2', class_='entry-title')
            
            if not articles:
                print("[*] No more articles found.")
                break

            for art in articles:
                link_tag = art.find('a', href=True)
                if link_tag:
                    art_url = link_tag['href']
                    print(f"  [+] Extracting: {art_url}")
                    data = self.extract_article_data(art_url)
                    if data:
                        all_data.append(data)
                        # Save incrementally
                        with open(output_file, 'a', encoding='utf-8') as f:
                            f.write(json.dumps(data, ensure_ascii=False) + "\n")
                        
                        # Optional: Download PDFs found in article
                        for pdf_url in data['pdf_links']:
                            self.download_pdf(pdf_url)
                    
                    time.sleep(1) # Polite crawling

            # Check if next page exists
            next_page = soup.find('a', class_='next page-numbers')
            if not next_page:
                break
            
            current_page += 1

        print(f"[*] Finished! Saved {len(all_data)} articles to {output_file}")

    def download_pdf(self, pdf_url: str):
        """Download file PDF."""
        file_name = pdf_url.split("/")[-1]
        save_path = self.pdf_dir / file_name
        
        if save_path.exists():
            return

        try:
            with requests.get(pdf_url, headers=self.headers, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"    [PDF] Saved {file_name}")
        except Exception as e:
            print(f"    [!] Failed PDF download: {e}")

    def get_all_categories(self) -> List[str]:
        """Find all category links under 'DOKUMEN GEREJA' menu."""
        soup = self.get_soup(self.base_url)
        if not soup:
            return []
        
        categories = []
        # Look for the 'DOKUMEN GEREJA' menu item and its sub-menu
        menu_items = soup.find_all('li', class_='menu-item')
        for item in menu_items:
            a = item.find('a')
            if a and 'DOKUMEN GEREJA' in a.get_text().upper():
                # Found the main menu, now get all links in its sub-menu
                sub_menu = item.find('ul', class_='sub-menu')
                if sub_menu:
                    for sub_a in sub_menu.find_all('a', href=True):
                        categories.append(sub_a['href'])
                # Also include the main category itself if it has a link
                if a['href'] != '#':
                    categories.append(a['href'])
        
        # Add some common ones manually just in case
        manual_cats = [
            "/category/seri-dokumen-gerejawi/",
            "/category/ensiklik/",
            "/category/pesan-paus/",
        ]
        for m in manual_cats:
            categories.append(urljoin(self.base_url, m))
        
        return list(set(categories))

    def run_full_crawl(self):
        """Crawl all discovered categories."""
        categories = self.get_all_categories()
        print(f"[*] Found {len(categories)} categories to crawl.")
        for cat in categories:
            print(f"[*] Starting crawl for category: {cat}")
            self.crawl_category(cat, max_pages=10) # 10 pages per cat is usually enough

if __name__ == "__main__":
    spider = KWISpider()
    spider.run_full_crawl()
