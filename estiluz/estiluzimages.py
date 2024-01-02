import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from time import sleep
import myfuncs
import time
options = webdriver.ChromeOptions()
options.add_extension("cookies.crx")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
start_time = time.time()
driver = webdriver.Chrome(options=options)
driver.maximize_window()
mainurl = "https://www.dropbox.com/sh/84nt89ljhzoo6m2/AACQtiqBFtW7-fdkp-AmR5yna/ESTILUZ%20IMAGES%20WEB?dl=0&subfolder_nav_tracking=1"

driver.get(mainurl)

def getphotos():
    alliconlinks = []
    allsurfaceimages = ['intentionally filled']
    while(len(alliconlinks) != len(allsurfaceimages)):
        sleep(5)
        alllinks = driver.find_elements(By.CSS_SELECTOR, "li._sl-card_1iaob_32 a")
        for link in alllinks:
            alliconlinks.append(link.get_attribute("href"))

        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li._sl-card_1iaob_32 img")))
        allsurfacess = driver.find_elements(By.CSS_SELECTOR, "li._sl-card_1iaob_32 img")
        allsurfaceimages = []
        for img in allsurfacess:
            allsurfaceimages.append(img.get_attribute("src"))

    
    for index in range(len(alliconlinks)):
        foto = {}
        surfaceimg = allsurfaceimages[index]
        driver.get(alliconlinks[index])
        #a webdriverwait for fotoadi
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav div._file-name-container_1rkjs_28 span.dig-Text--isBold")))
        #a webdriverwait for fullfoto
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div._layer_1vnnd_41 img._fullSizeImg_1vnnd_16")))
        
        
        fotoadi = driver.find_element(By.CSS_SELECTOR, "nav div._file-name-container_1rkjs_28 span.dig-Text--isBold").text
        fullfoto = driver.find_element(By.CSS_SELECTOR, "div._layer_1vnnd_41 img._fullSizeImg_1vnnd_16").get_attribute("src")
        
        foto["foto_adi"] = fotoadi
        foto["surface_image"] = surfaceimg
        foto["full_foto"] = fullfoto
        data[fotoadi] = foto
        

WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.dig-Table-body div.dig-Table-row a")))
allfolderlinks = driver.find_elements(By.CSS_SELECTOR, "div.dig-Table-body div.dig-Table-row a")
allfolderurls = []
for link in allfolderlinks:
    allfolderurls.append(link.get_attribute("href"))
    
data = {}

for folderlink in allfolderurls:
    driver.get(folderlink)
    

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li._sl-card_1iaob_32 a")))
        getphotos()
    except:
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.dig-Table-body div.dig-Table-row a")))
        insidefolders = driver.find_elements(By.CSS_SELECTOR, "div.dig-Table-body div.dig-Table-row a")
        insidefolderurls = []
        for link in insidefolders: 
            insidefolderurls.append(link.get_attribute("href"))
        for folderlink in insidefolderurls:
            driver.get(folderlink)
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li._sl-card_1iaob_32 a")))
                getphotos()
            except:
                #a webdriverwait for fotoadi
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav div._file-name-container_1rkjs_28 span.dig-Text--isBold")))
                #a webdriverwait for fullfoto
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div._layer_1vnnd_41 img._fullSizeImg_1vnnd_16")))
                
                foto = {}
                
                fotoadi = driver.find_element(By.CSS_SELECTOR, "nav div._file-name-container_1rkjs_28 span.dig-Text--isBold").text
                fullfoto = driver.find_element(By.CSS_SELECTOR, "div._layer_1vnnd_41 img._fullSizeImg_1vnnd_16").get_attribute("src")
                
                foto["foto_adi"] = fotoadi
                foto["surface_image"] = "xxsurfaceimgxx"
                foto["full_foto"] = fullfoto
                data[fotoadi] = foto
    
    

def tofile():
    with open("estiluzimages.json", 'w', encoding="utf-8") as outfile:
        json.dump(data, outfile, indent=2, ensure_ascii=False)

tofile()

print("---elapsed time: %s minutes ---" % ((time.time() - start_time) // 60))

