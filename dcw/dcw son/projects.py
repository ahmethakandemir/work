import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from time import sleep
import time

start_time = time.time()

options = webdriver.ChromeOptions()
options.add_extension("cookies.crx")
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=options)
driver.maximize_window()
mainurl = "https://dcw-editions.fr/en/projets"
photoUrlBeginning = "https://dcw-editions.fr"
#write a function to write the errors to the log.txt file we will append to it every error

jsondata = {}

open('log.txt','w',).close()
log = open('log.txt','a', encoding="utf-8")

def tofile(jsondata):
    with open('dcw_projects_data.json', 'w', encoding="utf-8") as outfile:
        json.dump(jsondata, outfile, indent=2, ensure_ascii=False)

driver.get(mainurl)

WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.dcw-card")))
cards = driver.find_elements(By.CSS_SELECTOR,"div.dcw-card")

for card in range(len(cards)):
    cards = driver.find_elements(By.CSS_SELECTOR,"div.dcw-card")
    cards[card].click()
    project_name = driver.find_elements(By.CSS_SELECTOR, "div.container > div.breadcrumb div > a")[1].text.strip()
    datas = driver.find_elements(By.CSS_SELECTOR, "div.page > div.entete div.item")
    
    project_link = driver.current_url
    jsondata[project_link] = project = {}
    project["project_link"] = project_link
    project["project_name"] = project_name
    linkler = []
    for data in datas:
        key = data.find_element(By.CSS_SELECTOR, "span").text.strip()
        try:
            data.find_element(By.CSS_SELECTOR, "a")
            allvalues = data.find_elements(By.CSS_SELECTOR, "a")
            value = ""
            for val in allvalues:
                linkler.append(val.get_attribute("href"))
                value = value + val.text.strip() + " / "
            value = value[:-3]
        except:
            value = data.text.strip().replace(key,"").strip()
        project[key] = value
    project["used_products_links"] = linkler
    
    
    
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.image div.content > div.legende")))
    soup = bs(driver.find_element(By.CSS_SELECTOR, "body").get_property("outerHTML"), "lxml")
    imagedivs = soup.select("div.image")
    images = {}
    for img in range(len(imagedivs)):
        imgurl = photoUrlBeginning + imagedivs[img].select_one("img").get("src")
        useds = imagedivs[img].select_one("div.content > div.legende").text.strip()
        
        images[f"{imgurl}"] = useds

    project["images"] = images

    
    driver.get(mainurl)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.dcw-card")))
driver.quit()

tofile(jsondata)