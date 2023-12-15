import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from time import sleep
import aileler
import time

start_time = time.time()

options = webdriver.ChromeOptions()
options.add_extension("cookies.crx")
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=options)
driver.maximize_window()
mainurl = "https://www.leebroom.com/lighting/"
#write a function to write the errors to the log.txt file we will append to it every error

jsondata = {}

urunfotocss = "div.col-md-6 div.owl-stage div.owl-item:not(.cloned)"

open('log.txt','w',).close()
log = open('log.txt','a', encoding="utf-8")



def tofile(jsondata):
    with open('data.json', 'w', encoding="utf-8") as outfile:
        json.dump(jsondata, outfile, indent=2, ensure_ascii=False)


driver.get(mainurl)
WebDriverWait(driver, 40).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.box > a > div > span > p")))
soup = bs(driver.find_element(By.CSS_SELECTOR, "body").get_property("outerHTML"), 'lxml')
allfamilies = soup.select("div.box > a > div > span > p")

allfamilieslist = []
for family in allfamilies:
    log.write(family.text.strip() + "\n")

driver.quit()
print("All families are collected in log.txt file")