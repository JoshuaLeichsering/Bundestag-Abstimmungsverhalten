from bs4 import BeautifulSoup as soup
import requests

html_object = requests.get("https://www.abgeordnetenwatch.de/bundestag/abstimmungen").text
soup_item = soup(html_object, 'html.parser')

for items in soup_item.find_all("a"):
    try:
        if items.span is not None:
            if items.span.string == "Letzte Seite":
                new_item = items.get("href")
    except Exception as e:
        continue

new_item = new_item[new_item.find("=")+1:]
print(new_item)
