import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.dmxs.org"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    )
}


def get_soup(url):
    resp = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )
    resp.raise_for_status()

    # 关键：直接解析原始 bytes，不使用 resp.text
    return BeautifulSoup(
        resp.content,
        "html.parser",
        from_encoding="gb18030"
    )


def get_chapter_urls(catalog_url):
    """从目录页获取所有章节链接"""
    soup = get_soup(catalog_url)

    chapter_urls = []

    for a in soup.select(".book_list a"):
        href = a.get("href")

        if href:
            chapter_urls.append(urljoin(BASE_URL, href))

    return chapter_urls


def get_chapter_content(url):
    resp = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )
    resp.raise_for_status()

    print("网站原始编码声明：", resp.encoding)
    print("自动猜测编码：", resp.apparent_encoding)

    html = resp.content.decode(
        "gb18030",
        errors="replace"
    )

    # 先检查手动解码是否成功
    print("手动解码后的 HTML：")
    print(html[:200])

    soup = BeautifulSoup(html, "html.parser")

    content_div = soup.select_one(".read_chapterDetail")

    if content_div is None:
        raise ValueError(f"未找到正文：{url}")

    paragraphs = content_div.find_all("p")

    return "\n".join(
        p.get_text(" ", strip=True)
        for p in paragraphs
    )


def save_to_txt(chapter_urls, filename="novel_fixed.txt"):
    # 使用全新的文件名，避免误开旧文件
    with open(filename, "w", encoding="utf-8-sig") as f:
        for i, url in enumerate(chapter_urls, start=1):
            print(f"正在爬第 {i} 章：{url}")

            try:
                content = get_chapter_content(url)

                # 第一次抓取时在终端检查内容
                if i == 1:
                    print("正文预览：")
                    print(content[:300])

                f.write(content)
                f.write("\n\n")
                f.flush()

            except Exception as exc:
                print(f"第 {i} 章抓取失败：{exc}")

            time.sleep(2)


if __name__ == "__main__":
    catalog_url = "https://www.dmxs.org/xhly/25208.html"
    chapter_urls = get_chapter_urls(catalog_url)
    print(f"共找到 {len(chapter_urls)} 章")

    if not chapter_urls:
        raise RuntimeError("没有找到任何章节，请检查目录地址或网页结构")

    save_to_txt(
        chapter_urls,
        filename="novel.txt"
    )