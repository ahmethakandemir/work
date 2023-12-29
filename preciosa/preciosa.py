import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from time import sleep
from myfuncs import addId
# import preciosa.aileler as aileler
import time

start_time = time.time()

options = webdriver.ChromeOptions()
options.add_extension("cookies.crx")
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=options)
driver.maximize_window()
mainurl = "https://eshop.preciosalighting.com/en/products/"
urlbeginning = "https://www.preciosalighting"
#write a function to write the errors to the log.txt file we will append to it every error

jsondata = {}

open('log.txt','w',).close()
log = open('log.txt','a', encoding="utf-8")

def tofile(jsondata):
    with open('data.json', 'w', encoding="utf-8") as outfile:
        json.dump(jsondata, outfile, indent=2, ensure_ascii=False)
        
def soruisaretisil(url):
    # we will delete the last question mark and everything after it
    if url.find("?") != -1:
        url = url[:url.find("?")]
    return url

driver.get(mainurl)
jsondata = {}

seri_linkleri = []
templinks = driver.find_elements(By.CSS_SELECTOR, "div.header-bottom > ul > li")
for i in range(4):
    seri_linkleri.append(templinks[i].find_element(By.CSS_SELECTOR, "a").get_attribute("href"))

for i in range(len(seri_linkleri)):
    driver.get(seri_linkleri[i])
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product-overlay > table tr a")))
    grupdivs = driver.find_elements(By.CSS_SELECTOR, "div.product-overlay > table tr a")
    gruplinkleri = []
    for j in range(len(grupdivs)):
        gruplinkleri.append(grupdivs[j].get_attribute("href"))
    
    for g in range(len(gruplinkleri)):
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product-item img")))
        grupcover = driver.find_elements(By.CSS_SELECTOR, "div.product-item img")[g].get_attribute("src")
        driver.get(gruplinkleri[g])
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.breadcrumb")))
        aile_adi = (driver.find_element(By.CSS_SELECTOR, "h2.text-colored").text).capitalize()
        seri_adi = aile_adi + " " + driver.find_elements(By.CSS_SELECTOR, "div.breadcrumb > a")[1].text.capitalize()
        grup_adi = seri_adi + " " + driver.find_element(By.CSS_SELECTOR, "div.text-center > div.headline-note").text.capitalize()
        if jsondata.get(aile_adi) == None:
            jsondata[aile_adi] = aile = {}
            aile["aile_data"] = aile_data = {}
            aile["seriler"] = {}
            aile_data["family_id"] = ""
            aile_data["family_name"] = aile_adi
        if jsondata[aile_adi]["seriler"].get(seri_adi) == None:
            jsondata[aile_adi]["seriler"][seri_adi] = seri = {}
            seri["seri_data"] = seri_data = {}
            seri["gruplar"] = {}
            seri_data["series_id"] = ""
            seri_data["series_name"] = seri_adi
        if jsondata[aile_adi]["seriler"][seri_adi]["gruplar"].get(grup_adi) == None:
            jsondata[aile_adi]["seriler"][seri_adi]["gruplar"][grup_adi] = grup = {}
            grup["grup_data"] = grup_data = {}
            grup_data["group_id"] = ""

        grup_data["group_name"] = grup_adi
        grup_data["group_link"] = driver.current_url
        grup_data["group_cover_photo"] = soruisaretisil(grupcover)
        try:
            driver.find_element(By.CSS_SELECTOR, "div.text-center > p").click()
        except:
            pass
        try:
            grup_data["group_description"] = driver.find_elements(By.CSS_SELECTOR, "div.perex p")[0].text.replace("\n"," ") + " " + driver.find_elements(By.CSS_SELECTOR, "div.perex p")[1].text.replace("\n"," ")
        except:
            log.write(f"Error taking group description: {driver.current_url}s\n")
            grup_data["group_description"] = ""
        if grup_data["group_description"] == " ":
            grup_data["group_description"] = ""
        
        grup["urunler"] = []
        allurunler = driver.find_elements(By.CSS_SELECTOR, "section.product-detail")
        for u in range(len(allurunler)):
            urun = {}
            wholediv = driver.find_elements(By.CSS_SELECTOR, "section.product-detail")[u]
            urundatadiv = driver.find_elements(By.CSS_SELECTOR, "section.product-detail table.table-product-data")[u]
            WebDriverWait(wholediv, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2.no-margin")))
            urun_adi = wholediv.find_element(By.CSS_SELECTOR, "h2.no-margin").text.strip()
            if len(allurunler) > 1:
                while urun_adi == "":
                    WebDriverWait(wholediv, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2.no-margin")))
                    urun_adi = wholediv.find_element(By.CSS_SELECTOR, "h2.no-margin").text.strip()
            elif len(allurunler) == 1:
                urun_adi = grup_adi
            else:
                print("Error taking product name")
            urun["product_name"] = urun_adi
            urun["product_id"] = ""
            technicaldata = {}
            for data in urundatadiv.find_elements(By.CSS_SELECTOR, "tr"):
                try:
                    key = data.find_element(By.CSS_SELECTOR, "th").text
                    value = data.find_element(By.CSS_SELECTOR, "td").text
                    if key == "" or value == "":
                        pass
                    else:
                        technicaldata[key] = value
                except:
                    pass    
            urun["technical_data"] = technicaldata
            #get the photos
            urunfotolar = []
            coverphoto = soruisaretisil(wholediv.find_element(By.CSS_SELECTOR, "section.product-detail div.lSSlideOuter li.lslide img").get_attribute("src"))
            try:
                wholediv.find_element(By.CSS_SELECTOR, "div.container div.row div.lSSlideOuter li.lslide.active a.open-gallery").click()
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.modal.gallery-modal.fade.in div.modal-body > div > ul.lSPager.lSGallery li img")))
                    photodivs = driver.find_elements(By.CSS_SELECTOR, "div.modal.gallery-modal.fade.in div.modal-body > div > ul.lSPager.lSGallery li img")
                    for photodiv in photodivs:
                        urunfotolar.append(soruisaretisil(photodiv.get_attribute("src")))
                except:
                    photodiv = driver.find_element(By.CSS_SELECTOR, "li > div > img.zoomImg")
                    urunfotolar.append(soruisaretisil(photodiv.get_attribute("src")))
                finally:
                    urun["photos"] = urunfotolar
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.modal.fade.in > div > div > div.modal-header > button > span")))
                    driver.find_element(By.CSS_SELECTOR, "div.modal.fade.in > div > div > div.modal-header > button > span").click()
            except:
                pass
            finally:
                urun["cover_photo"] = coverphoto
                
            
            grup["urunler"].append(urun)
            
        driver.get(seri_linkleri[i])


driver.quit()

addId(jsondata,700007)
tofile(jsondata)
log.close()
minutes, seconds = divmod(int(time.time() - start_time), 60)
print(f"Elapsed time: {minutes} min {seconds} sec")