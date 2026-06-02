# for 69shuba
# get chapter links from a website catalog page
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By

url = "https://www.69shuba.com/book/43256/"
headers = {
    "User-Agent": "Mozilla/5.0"
}

driver = webdriver.Chrome()
driver.get(url)


# html = requests.get(url, headers=headers).text
# soup = BeautifulSoup(html, "html.parser")


# catalog = soup.find("div", id="catalog")
# if catalog is None:
#     catalog = soup.find("div", id="list")


# get chapter links
chapter_links = driver.find_elements(By.CSS_SELECTOR, "#catalog a")


with open("chapters.txt", "w", encoding="utf-8") as f:
    for a in chapter_links:
        # remove invalid links
        if "第" not in a.text:
            continue
        f.write(urljoin(url, a.get_attribute("href")) + "\n")