#!/usr/bin/python

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os

url = "https://www.reddit.com/r/greentext/"
path = os.getcwd()
cur_path = "webdriver"
sel_path = os.path.join(path, cur_path)

driver = webdriver.Firefox(sel_path)
options = webdriver.FirefoxOptions()
options.add_argument("--headless")
driver.get(url)

time.sleep(5)

html = driver.page_source

soup_item = BeautifulSoup(html, 'html.parser')

for elements in soup_item.find_all("img"):
    try:
        image_url = elements.get("src")
        print(image_url)
    except Exception as e:
        continue

driver.close()
