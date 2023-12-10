import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from time import sleep
import aileler


options = webdriver.ChromeOptions()
options.add_extension("cookies.crx")
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=options)
driver.maximize_window()
mainurl = "https://dcw-editions.fr/en/collections"
photoUrlBeginning = "https://dcw-editions.fr"
#write a function to write the errors to the log.txt file we will append to it every error


driver.get(mainurl)


webdriverwait = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.dcw-card')))
soup = bs(driver.find_element(By.CSS_SELECTOR,'body').get_property('outerHTML'), 'lxml')
familydivs = soup.select_one('div.thumbs-list')
familydivs = familydivs.select('div.dcw-card')
familynames = []
# limit familydivs to 2
for familydiv in familydivs:
    familynames.append(familydiv.select_one('h1.collection').text.strip())

driver.quit()