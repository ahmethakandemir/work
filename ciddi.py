import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup as bs
from time import sleep
import requests

url = "https://www.iguzzini.com"




# driver.get(url)

# sleep(2)

alljson = {}

link = requests.get(url)
lim = 1

ana_link = bs(link.content, "html.parser").find_all("div", {"class" : "grid-item col-12 col-xs-6 col-sm-4 col-md-3"}, limit=lim)
# ana link = butun kategorileri tutan class listesi


kategori = []
seriList = []
grupList = []
urunList = []

for i in range(lim):
    kategoriUrl = ana_link[i].find("a")["href"]
    kategoriName = ana_link[i].find("strong") #Indoor
    kategori.append(kategoriName)
    newUrl = url + kategoriUrl
    newLink = requests.get(newUrl)
    kategoriSoup = bs(newLink.content, "html.parser").find_all("li", {"class" : "grid-item col-1_2 col-xs-1_2 col-sm-1_3 col-md-1_4 col-lg-1_5"}, limit=lim)
    for k in range(lim):
        seriadi = kategoriSoup[k].find("div",{ "class" : "cp-product-list__thumb__label line"})
        seriList.append(seriadi)
        seriUrl = kategoriSoup[k].find("a")["href"]
        seriUrl = url + seriUrl
        seriLink = requests.get(seriUrl)
        seriSoup = bs(seriLink.content, "html.parser").find_all("div", {"class" : "grid-item col-1_2 col-xs-1_2 col-sm-1_3 col-md-1_4 col-lg-1_5"}, limit=lim)
        for s in range(lim):
            grupadi = seriSoup[s].find("span").text
            grupList.append(grupadi)
            grupUrl = seriSoup[s].find("a")["href"]
            grupUrl = url + grupUrl
            grupLink = requests.get(grupUrl)
            
            options = webdriver.ChromeOptions()
            options.add_extension("cookies.crx")
            driver = webdriver.Chrome(options=options)
            driver.get(grupUrl)
            sleep(2)
            driver.find_element(By.XPATH, "//*[@id='form']/div[4]/div[2]/div/div/div[2]/div[3]/div[2]/div/div/div/div[2]/div/div[1]/div[2]/div[2]/div[2]/table/tbody/tr[2]/td[3]/a").click()
            grupSoup = bs(driver.page_source, "html.parser")
            for g in range(lim):
                urunUrl = driver.current_url
                # sondan bir onceki / nin yanina bir tane daha / koymak icin
                urunUrl = urunUrl.replace("com/", "com//")
                urunSoup = bs(urunUrl, "html.parser")
                

# print(kategori)
# print(seriList)
# print(grupList)


 
                
                
                
                
                
                
                
                

                
                
                
                
# sleep(50)
                
# driver.close()

# for k in range(limitation):
#     kategoriler = {}
#     kategoriName = ana_link[k].find("a").find("h3").text.strip()
#     kategoriler[kategoriName] = []
#     print(kategoriName)
#     newlink = requests.get(newurl)
#     kategorisoup = bs(newlink.content, "html.parser")
    
#     for s in range(limitation):
#         serilerdiv = kategorisoup.find_all("li", {"class" : "grid-item col-1_2 col-xs-1_2 col-sm-1_3 col-md-1_4 col-lg-1_5"}, limit=limitation)
#         seri = serilerdiv[s].find("a")["href"]
#         print("   ",seri)
#         seriurl = url + seri
#         print(seriurl)
#         serilink = requests.get(seriurl)
#         serisoup = bs(serilink.content, "html.parser")
#         for pt in range(limitation):
#             productType = serisoup.find_all("div", {"class" : "cp-product-list__thumb__label group"}, limit=limitation)
#             productType = productType[pt].find("a")["href"]
#             print("      ",productType) # /cyrstal genelal lighting
#             productTypeurl = url + productType
#             productTypelink = requests.get(productTypeurl)
#             productTypesoup = bs(productTypelink.content, "html.parser")
#             for p in range(limitation):
#                 product = productTypesoup.find_all("td", {"class" : "prod-table__col"}, limit=limitation)
#                 print("\n\n",product)
#                 product = product[p].find("a")["href"]
#                 producturl = url + product
#                 productlink = requests.get(producturl)
#                 productsoup = bs(productlink.content, "html.parser")


# title = driver.find_element(By.XPATH, "//*[@id='form']/div[4]/div[2]/div/div/div[2]/div[1]/div/div[1]/a/h3/strong")

# element = driver.find_element(By.XPATH, "//*[@id='form']/div[4]/div[2]/div/div/div[2]/div[1]/div/div[1]/a")
# element.click()
# newurl = driver.current_url
# newlink = requests.get(newurl)
# soup = bs(newlink.content, "html.parser")


# seriler = soup.find("div", {"class" : "cp-product-list grid-section constrain"}).find_all("div", {"class" : "cp-product-list__thumb__label line"})
# for i in seriler:
#     seriList.append(i.text.strip())
# # crystale giriyor

# element = driver.find_element(By.XPATH, "//*[@id='form']/div[4]/div[2]/div/div/div[2]/div[1]/div[2]/ul[1]/li[2]/a")
# element.click()

# newurl = driver.current_url
# newlink = requests.get(newurl)
# soup = bs(newlink.content, "html.parser")

# gruplar = list(soup.find_all("span", {"class" : "subtitle"}))
# gruplar2 = list(map(lambda x: x.text, gruplar))
# print(gruplar2)
# gruplist = gruplar2

# # crystal genel aydinlatma giriyor
# element = driver.find_element(By.XPATH, "//*[@id='form']/div[4]/div[2]/div/div/div[2]/div[4]/div/ul/div[1]/div/div[2]/a")
# element.click()



# element = driver.find_element(By.XPATH, "//*[@id='form']/div[4]/div[2]/div/div/div[2]/div[3]/div[2]/div/div/div/div[2]/div/div[1]/div[2]/div[2]/div[2]/table/tbody/tr[2]/td[2]/a")
# element.click()

# kategori[f"{title.text}"] = title.text

# currentUrl = driver.current_url
# print(currentUrl)