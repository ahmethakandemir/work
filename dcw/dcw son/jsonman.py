import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from time import sleep
import aileler as aileler
import time

start_time = time.time()

options = webdriver.ChromeOptions()
options.add_extension("cookies.crx")
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=options)
driver.maximize_window()
mainurl = "https://dcw-editions.fr/en/telechargements/3d"
jsondata = {}

def tofile(jsondata):
    with open('data.json', 'w', encoding="utf-8") as outfile:
        json.dump(jsondata, outfile, indent=2, ensure_ascii=False)


driver.get(mainurl)