import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from time import sleep
import myfuncs
import time

start_time = time.time()

options = webdriver.ChromeOptions()
options.add_extension("cookies.crx")
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=options)
driver.maximize_window()
mainurl = "https://www.estiluz.com/en/collections"

#write a function to write the errors to the log.txt file we will append to it every error

jsondata = {}

open('log.txt','w',).close()
log = open('log.txt','a', encoding="utf-8")

driver.get("https://www.estiluz.com/en/downloads")


driver.get(mainurl)


WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.main_content.container-fluid div.item")))
soup = bs(driver.find_element(By.CSS_SELECTOR, "body").get_property("outerHTML"), "lxml")
allfamiliesdivs = soup.select("div.main_content.container-fluid div.item")
for familydiv in allfamiliesdivs:
    aile_adi = familydiv.select_one("a div p.name-title").text
    aile_designer = familydiv.select_one("a div p.page-description").text.replace("by ","")
    aile_img = familydiv.select_one("a img")['src']
    jsondata[aile_adi] = aile = {}
    jsondata[aile_adi]["aile_data"] = ailedata = {}
    jsondata[aile_adi]["seriler"] = {}
    
    ailedata["family_name"] = aile_adi
    ailedata["family_id"] = ""
    ailedata["family_url"] = family_url = familydiv.select_one("a")['href']
    ailedata["family_designer"] = aile_designer
    ailedata["family_surface_image"] = aile_img
    ailedata["family_inner_image"] = ""
    driver.get(family_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.main_content div.text-center > img")))
    aile_inner_img = driver.find_element(By.CSS_SELECTOR, "div.main_content div.text-center > img").get_attribute("src")
    aile_description = driver.find_elements(By.CSS_SELECTOR, "div.main_content div.text-center div.pb-5 p:not(.family-description)")
    ailedata["family_inner_image"] = aile_inner_img
    desc = ""
    for p in aile_description:
        desc += p.text.replace("\n"," ")
    ailedata["family_description"] = desc
    soup2 = bs(driver.find_element(By.CSS_SELECTOR, "body").get_property("outerHTML"), "lxml")
    gruplardivs = soup2.select("div.main_content.container-fluid div.row.mb-5 div.px-5 a")
    for grupdiv in gruplardivs:
        grupadi = grupdiv.select_one("p").text.strip()
        grup_img = grupdiv.select_one("img")['src']
        gruplink = grupdiv['href']
        
        driver.get(gruplink)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.col-md-12 li:nth-child(2) a span")))
        seriadi = driver.find_element(By.CSS_SELECTOR, "div.col-md-12 li:nth-child(2) a span").text

        
        if seriadi in aile["seriler"]:
            seri = aile["seriler"][seriadi]
        else:
            aile["seriler"][seriadi] = seri = {}
            seri["seri_data"] = seridata = {}
            seridata["series_name"] = seriadi
            seridata["series_id"] = ""
            seridesc = driver.find_elements(By.CSS_SELECTOR, "div.text-center div.pb-5 p:not(.family-description)")
            desc = ""
            for p in seridesc:
                desc += p.text.replace("\n"," ")
            
            seri["gruplar"] = {}
            
        if grupadi in seri["gruplar"]:
            grup = seri["gruplar"][grupadi]
        else:    
            seri["gruplar"][grupadi] = grup = {}
            grup["grup_data"] = grupdata = {}
            grupdata["group_name"] = grupadi
            grupdata["group_id"] = ""
            grupdata["group_url"] = gruplink
            grupdata["group_surface_image"] = grup_img
            grup["urunler"] = []
            
        ##grup desc alinacak
        
        urunler = []
        
        urunlerdivs = driver.find_elements(By.CSS_SELECTOR, "div.tech_div.px-3.py-5")
        for urundiv in urunlerdivs:
            urun = {}
            urun_adi = urundiv.find_element(By.CSS_SELECTOR, "p.product-section-title").text.strip()
            urun["product_name"] = urun_adi
            urun["product_id"] = ""
            try:
                urun_schema = urundiv.find_element(By.CSS_SELECTOR, "div.text-center img").get_attribute("src")
                urun["product_schema"] = urun_schema
            except:
                pass
            
            divs = urundiv.find_elements(By.CSS_SELECTOR, "div.col-md-3.pt-5")
            
            for div in divs:
                value = []
                title = div.find_element(By.CSS_SELECTOR,"p.product-spec-title")
                try:    
                    technicalinfos = div.find_elements(By.CSS_SELECTOR,"div.product-spec-information p")
                    if technicalinfos == []:
                        raise("technical")    
                    for info in technicalinfos:
                        value.extend(info.text.split("\n"))
                    urun[title.text] = value
                    continue
                except:
                    pass
                
                try:
                   
                    finishinfosdivs = div.find_elements(By.CSS_SELECTOR,"div.col-6")
                    for finishdiv in finishinfosdivs:
                        valueslist = []
                        colornameslist = finishdiv.find_element(By.CSS_SELECTOR,"p.product-spec-finish").text.split("\n")
                        values = finishdiv.find_elements(By.CSS_SELECTOR,"p.product-spec-finish i")
                        colorindex = 0
                        for value in values:
                            temp = {}
                            code = value.get_attribute("style").replace("background-color: ","").replace(";","")
                            colorname = value.text
                            temp["color_name"] = colornameslist[colorindex]
                            temp["color_code"] = code
                            valueslist.append(temp)
                            colorindex += 1
                        urun[title.text] = valueslist
                    continue
                except:
                    pass
            
            
            
            
            iconsdiv = urundiv.find_elements(By.CSS_SELECTOR, "div.icons img")
            icons = [img.get_attribute('src') for img in iconsdiv]
            
            
            try:
                downlinks = urundiv.find_elements(By.CSS_SELECTOR, "a.btn")
                if len(downlinks) != 0:
                    urun["downloads"] = downloads = {}
                for downlink in downlinks:
                        link = downlink.get_attribute("href")
                        if "dropbox" in link:
                            pass
                        elif downlink.text.strip() == "More documents":
                            pass
                        else:
                            filename = downlink.text.strip()
                            downloads[filename] = link 
            except:
                pass

            
            urun["product_icons"] = icons
            urunler.append(urun)
        grup["urunler"].extend(urunler)
            
        





driver.quit()
log.close()
myfuncs.addId(jsondata,700008)

myfuncs.tofile(jsondata)
# print time passed as minutes and seconds
print("--- %s" % ((time.time() - start_time)/60))
print("--- %s" % ((time.time() - start_time)%60))
print("Finished")