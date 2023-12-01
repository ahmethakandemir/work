import requests
import json
from bs4 import BeautifulSoup as bs

url = "https://www.n11.com/telefon-ve-aksesuarlari"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
link = requests.get(url=url, headers=headers).content
soup = bs(link, "html.parser")

html = soup.body.find_all("li", {"class": "column"} )

# Extract the text content of the <h3> elements


all = []

count = 0
for li in html:
    new_dict = {
        "name": li.a.get("title"),
        "link": li.a.get("href")
    }
    all.append(new_dict)
    count += 1

with open("n11.json", "w", encoding='utf-8') as file:
    json.dump(all, file, indent=4, ensure_ascii=False)


# with open("n11.json", "w", encoding='utf-8') as file:
#     json.dump(html_list, file, indent=4, ensure_ascii=False)