# get chapter content from a list of urls and save to a file
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options


options = Options()
options.headless = True


def fetch_chapter_selenium(driver, url):
    driver.get(url)

    # 等待 txtnav 出现
    txtnav_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.txtnav"))
    )

    # 标题
    try:
        title_elem = txtnav_div.find_element(By.TAG_NAME, "h1")
        title = title_elem.text.strip()
    except:
        title = "未知章节"

    # 删除页面顶部的章节标题和作者信息，防止重复
    for elem in txtnav_div.find_elements(
        By.CSS_SELECTOR, "h1.hide720, div.txtinfo.hide720"
    ):
        driver.execute_script("arguments[0].remove();", elem)

    # 删除广告 div
    for ad_div in txtnav_div.find_elements(By.CSS_SELECTOR, "#txtright, .contentadv, .bottom-ad"):driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
    """, ad_div)


    # 删除 script 标签
    for script in txtnav_div.find_elements(By.TAG_NAME, "script"):
        driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
        """, script)

    # 获取剩余文本
    content = txtnav_div.text.strip()

    return title, content


def build_book_selenium(link_file, output_file, start_index=1):
    # default driver
    driver = webdriver.Chrome()

    with open(link_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    if not 1 <= start_index <= len(urls):
        raise ValueError(f"起始序号必须在 1 到 {len(urls)} 之间")

    with open(output_file, "w", encoding="utf-8") as book:
        for i, url in enumerate(urls[start_index - 1:], start_index):
            print(f"get {i}/{len(urls)}: {url}")

            try:
                title, content = fetch_chapter_selenium(driver, url)
            except Exception as e:
                print("fail:", url, e)
                continue

            book.write(content + "\n\n\n")

            time.sleep(0.5) 

    driver.quit()



if __name__ == "__main__":
    filename = "chapters.txt"
    output = "output.txt"
    start_input = input("从第几个链接开始读取？（直接回车默认从第1个开始）：").strip()
    try:
        start_index = int(start_input) if start_input else 1
    except ValueError:
        raise ValueError("请输入有效的整数序号")

    build_book_selenium(filename, output, start_index)
