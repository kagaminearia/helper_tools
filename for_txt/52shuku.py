import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


def fetch_html(url: str) -> str:
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=(5, 15),
    )
    response.raise_for_status()

    response.encoding = response.apparent_encoding
    return response.text


def parse_chapter_links(index_html: str, base_url: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(index_html, "html.parser")

    chapters = []

    for a in soup.select("ul.list.clearfix li.mulu a"):
        title = a.get_text(strip=True)
        href = a.get("href")

        if not href:
            continue

        full_url = urljoin(base_url, href)
        chapters.append((title, full_url))

    return chapters


def parse_chapter_text(chapter_html: str) -> tuple[str, str]:
    soup = BeautifulSoup(chapter_html, "html.parser")

    title_tag = soup.select_one("h1#nr_title")
    title = title_tag.get_text(strip=True) if title_tag else "未知章节"

    article = soup.select_one("article#nr1")
    if article is None:
        return title, ""

    # 先找到分页栏
    pagination = article.select_one("div.pagination2")

    # 删除分页栏以及它后面的所有内容
    if pagination is not None:
        for sibling in list(pagination.next_siblings):
            sibling.extract()
        pagination.extract()

    paragraphs = []

    for p in article.find_all("p"):
        text = p.get_text("", strip=True)

        if not text:
            continue

        skip_keywords = [
            "哦豁，小伙伴们如果觉得52书库不错",
            "传送门：",
        ]

        if any(keyword in text for keyword in skip_keywords):
            continue

        paragraphs.append(text)

    return title, "\n\n".join(paragraphs)


def scrape_novel(index_url: str, output_path: str, start_chapter: int = 1) -> None:
    index_html = fetch_html(index_url)
    chapter_links = parse_chapter_links(index_html, index_url)
    print("HTML length:", len(index_html))
    print("First 500 chars:")
    print(index_html[:500])

    print("Found chapter links:", len(chapter_links))

    # 从指定章节开始
    chapter_links = chapter_links[start_chapter - 1:]

    print(f"Found {len(chapter_links)} pages")

    output_file = Path(output_path)

    with output_file.open("w", encoding="utf-8") as f:
        for i, (page_title, page_url) in enumerate(chapter_links, start=start_chapter):
            print(f"[{i}] {page_title}: {page_url}")

            try:
                chapter_html = fetch_html(page_url)
                real_title, text = parse_chapter_text(chapter_html)

                if not text:
                    print(f"  Warning: no text found")
                    continue

                f.write("\n")
                f.write(text)
                f.write("\n")

                time.sleep(6)

            except requests.RequestException as e:
                print(f"  Request failed: {e}")

if __name__ == "__main__":
    index_url = "https://www.52shuku.net/jiakong/17_b/bkeF2.html"
    scrape_novel(index_url, "novel.txt")