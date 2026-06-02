import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.dmxs.org"  # website url

def get_chapter_urls(catalog_url):
    """从目录页获取所有章节链接"""
    resp = requests.get(catalog_url)
    resp.encoding = resp.apparent_encoding # encoding choice
    # resp.encoding = 'gb18030'

    soup = BeautifulSoup(resp.text, 'html.parser')

    chapter_urls = []
    for a in soup.select(".book_list a"):
        href = a.get("href")
        full_url = BASE_URL + href
        chapter_urls.append(full_url)

    return chapter_urls


def get_chapter_content(url):
    """获取单章内容"""
    resp = requests.get(url)
    resp.encoding = resp.apparent_encoding

    soup = BeautifulSoup(resp.text, 'html.parser')

    content_div = soup.select_one(".read_chapterDetail")

    paragraphs = content_div.find_all("p")
    text = "\n".join(p.get_text(strip=True) for p in paragraphs)

    return text


def save_to_txt(chapter_urls, filename="novel.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for i, url in enumerate(chapter_urls):
            print(f"正在爬第{i+1}章: {url}")

            content = get_chapter_content(url)

            f.write(f"\n\n")
            f.write(content)

            time.sleep(2)


if __name__ == "__main__":
    catalog_url = "https://www.dmxs.org/gdjk/3224.html"

    chapter_urls = get_chapter_urls(catalog_url)

    save_to_txt(chapter_urls)
