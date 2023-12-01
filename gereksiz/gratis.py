from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
from bs4 import BeautifulSoup as bs
import json

url = "https://www.gratis.com/cilt-bakim-c-502?page=1"

driver = webdriver.Firefox()
driver.get(url)
time.sleep(1)

productCards = []

for i in range(1, 5):
    link = requests.get(driver.current_url)
    soup = bs(link.content, "html.parser")
    products = soup.find_all("div", {"class": "product-cards"})

    for product in products:
        title = product.find("div", {"class": "infos"}).find("a").find("h5", {"class": "title"}).text.strip()
        
        price = product.find("div", {"class": "product-price"})
        tl = price.find_all("span")
        price = tl[0].text.strip()
        kurus = tl[1].text.replace(",","").strip()
        
        
        temp_dict = {
            "title": title,
            "price": f"{price}.{kurus}",
            "page": i
        }
        productCards.append(temp_dict)

    next_button = driver.find_element(By.XPATH, "//a[@class='type-next']")
    driver.execute_script("arguments[0].click();", next_button)
    time.sleep(1)

driver.quit()

with open("gratis.json", "w", encoding="utf-8") as file:
    json.dump(productCards, file, indent=4, ensure_ascii=False)