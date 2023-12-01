import requests
from bs4 import BeautifulSoup
import json

url = "https://www.watsons.com.tr/parfum/c/100013"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

html = requests.get(url=url, headers=headers).content

soup = BeautifulSoup(html, "html.parser")

markalar = soup.body.find_all("h3", {"class": "seo-content-wrapper"})

list_of_markalar = []




for i in range(1, 6):
    url = url + f"?page={i}"
    html = requests.get(url=url, headers=headers).content
    soup = BeautifulSoup(html, "html.parser")
    markalar = soup.body.find_all("h3", {"class": "seo-content-wrapper"})
    
    with open("markalar.json", "a+", encoding='utf-8') as file:
        for marka in markalar:
            list_of_markalar.append(marka.text)
        json.dump(list_of_markalar, file, indent=4, ensure_ascii=False)
        
with open("markalar.json", "r", encoding='utf-8') as file:
    file_data = file.read()
    file_data = file_data.replace("\n][\n",",\n\n")
with open("markalar.json", "w", encoding='utf-8') as file:
    file.write(file_data)