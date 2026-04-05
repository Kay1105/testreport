import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
import chardet

def is_same_domain(base_url, target_url):
    base_domain = urlparse(base_url).netloc
    target_domain = urlparse(target_url).netloc
    return base_domain == target_domain

def get_links(url, base_url):
    links = []
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            encoding = chardet.detect(response.content)['encoding']
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding=encoding)
            for a_tag in soup.find_all('a', href=True):
                link = urljoin(url, a_tag['href'])
                if is_same_domain(base_url, link):
                    links.append(link)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
    return links

def save_html(url, output_dir):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            encoding = chardet.detect(response.content)['encoding']
            html_text = response.content.decode(encoding, errors='replace')
            parsed = urlparse(url)
            safe_path = parsed.path.replace('/', '_') or '_root'
            safe_query = parsed.query.replace('=', '_').replace('&', '_')
            file_name = f"{parsed.netloc}{safe_path}_{safe_query}.html" if safe_query else f"{parsed.netloc}{safe_path}.html"

            file_path = os.path.join(output_dir, file_name)
            os.makedirs(output_dir, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_text)

            print(f"Saved: {file_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error saving {url}: {e}")

def crawl_domain(start_url, output_dir="downloaded_pages"):
    visited = set()
    to_visit = [start_url]

    while to_visit:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        save_html(url, output_dir)
        time.sleep(1)

        new_links = get_links(url, start_url)
        for link in new_links:
            if link not in visited:
                to_visit.append(link)

    print("クロール完了")

if __name__ == "__main__":
    start_url = "https://www.tysons.jp/tyharbor/"
    crawl_domain(start_url)