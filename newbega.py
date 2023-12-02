import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from time import sleep

options = webdriver.ChromeOptions()
options.add_extension("cookies.crx")
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=options)
driver.maximize_window()
mainurl = "https://www.bega.com/en/products/"

jsonlist = {}

def tofile(jsonlist):
    with open('bega.json', 'w', encoding='utf-8') as f:
        json.dump(jsonlist, f, ensure_ascii=False, indent=4)


driver.get(mainurl)
sleep(1)



soup = bs(driver.page_source, "lxml")
aile_isimleri = soup.select("div.grid.grid-cols-2")



for aile_ismi_index in range(2): # range(len(aile_isimleri))
    # Create a new soup object for each iteration
    soup = bs(driver.page_source, "lxml")
    aile_isimleri = soup.select("div.grid.grid-cols-2")    
    # jsonliste aile adını ekledik
    
    if(aile_ismi_index == 0):
        aileadi = "Outdoor Luminaries"
    elif(aile_ismi_index == 1):
        aileadi = "Indoor Luminaries"
    
    jsonlist[aileadi] = {}  
    aile = jsonlist[aileadi]
    
    # jsonda aileye data listesi ekledik
    aile["data"] = {}
    aile["seriler"] = {}
    
    seriler = aile_isimleri[aile_ismi_index].select(".relative")
    
    for seriindex in range(2): #range(len(seriler))
        seriler = aile_isimleri[aile_ismi_index].select(".relative")
        
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'relative.overflow-hidden.rounded.group.hover-zoom.z-0.bg-gray-darker')))
        seriler_clickable = driver.find_elements(By.CSS_SELECTOR,"div.grid.grid-cols-2 > .relative")
        seriler_clickable[seriindex + (16 * aile_ismi_index)].click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
        # serinin adini al
        soup2 = bs(driver.page_source, "lxml")
        seri_adi = soup2.select("h1.mb-0 span")
        seri_adi = seri_adi[0].text.strip()
        aile["seriler"][seri_adi] = {}
        seri = aile["seriler"][seri_adi]

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.hidden > div >.contents.rich-text p")))
            seri_data = soup2.select_one("div.hidden > div >.contents.rich-text p")
            seri_data = seri_data.text.strip()
            seri["seri data"] = seri_data  # recessed wall luminaires h1 inin altindaki text
        except Exception as e:
            print(e)
            print(seri_adi, " seri data bulunamadi")
            seri["data"] = {}

        seri["gruplar"] = {}  # gruplar
        # grup datasi al
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.grid.grid-cols-2")))
        soup3 = bs(driver.page_source, "lxml")
        gruplar = soup3.select("div.grid.grid-cols-2")
        
        myrange = 2 
        if len(gruplar) < 2:
            myrange = len(gruplar) 
        
        for grupindex in range(len(gruplar)): #range(len(gruplar))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.grid.grid-cols-2")))
            gruplar = soup3.select("div.grid.grid-cols-2")
            grup_adi = gruplar[grupindex].select_one("h5").text.strip()
            seri["gruplar"][grup_adi] = {}
            grup = seri["gruplar"][grup_adi]
            grup["grup data"] = {}
            grup["alt gruplar"] = {}
            altgruplar = grup["alt gruplar"]
            serilink = driver.current_url
            gruplarclickable = driver.find_elements(By.CSS_SELECTOR,"div.grid.grid-cols-2 > .rounded")
            for grupclickableindex in range(len(gruplarclickable)): #range(len(gruplarclickable))
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"div.grid.grid-cols-2 > .rounded")))
                gruplarclickable = driver.find_elements(By.CSS_SELECTOR,"div.grid.grid-cols-2 > .rounded")
                gruplarclickable[grupclickableindex].click()
                soup4 = bs(driver.find_element(By.CSS_SELECTOR,'body').get_property('outerHTML'), 'lxml')
                
                altgrupadi = soup4.select_one("div.text-white > h1 > span").text.strip()
                altgruplar[altgrupadi] = {}
                
                altgruplar[altgrupadi]["alt grup data"] = {}
                altgrupdata = altgruplar[altgrupadi]["alt grup data"]
                altgruplar[altgrupadi]["modeller"] = {}
                modeller = altgruplar[altgrupadi]["modeller"]

                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'div.tabs__item_active'))) ## cogulluk tekillik sorunu
                    soup4 = bs(driver.find_element(By.CSS_SELECTOR,'body').get_property('outerHTML'), 'lxml')
                    modelinadi = soup4.select_one("div.tabs__item_active").text.strip()
                except:
                    modelinadi = "modelin adi yok"
                finally:
                    modeller[modelinadi] = {}
                    model = modeller[modelinadi]
                    model["urunler"] = {}
                    model["model data"] = {}
                    modeldata = model["model data"]
                
                altgrupurl = driver.current_url
                altgrupdata["alt grup url"] = altgrupurl
                
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'section.scroll-mt-10 > div > div > div > p')))
                generalinfos = []

                #get technical infos div
                technicalinfos = []
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'div.mx-auto > div.w-full > div.mx-auto > div.max-w-60ch > div.contents')))
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'div#technical-data div.contents span.contents > span')))
                soup4 = bs(driver.find_element(By.CSS_SELECTOR,'body').get_property('outerHTML'), 'lxml')
                infos = soup4.find_all('div', attrs={'class': 'max-w-60ch md:max-w-75ch'})

                generalinfosdiv = infos[5].find_all('p') ## cozum duzeltilecek ##

                technicalinfosdiv = soup4.select('div#technical-data div.contents span.contents')
                
                
                for t in technicalinfosdiv:
                    t = t.text.split(" \n")
                    for t1 in t:
                        if t1.strip() != "":
                            if t1.strip() in technicalinfos:
                                pass
                            else:
                                technicalinfos.extend(t1.split(" \n"))
                
                #same for general infos
                for g in generalinfosdiv:
                    g = g.text.split(" \n")
                    for g1 in g:
                        if g1.strip() != "":
                            if g1.strip() in generalinfos:
                                pass
                            else:
                                generalinfos.extend(g1.split(" \n"))
                
                imagegallery = soup4.find_all('div', attrs={'class': 'mb-4 bg-transparent text-primary'})
                imagegallerylist = []
                for img in imagegallery:
                    imgurl = img.find('source').get('data-srcset')
                    imagegallerylist.append(imgurl)
            
                techimg1 = driver.find_element(By.CSS_SELECTOR,'div.h-full.relative.pb-8 > div > div  picture > source').get_attribute('data-srcset')
                techimg2 = driver.find_element(By.CSS_SELECTOR,'div.w-full.h-full.flex.justify-center > div picture > source').get_attribute('data-srcset')
                technicalimages = [techimg1, techimg2]
        

                altgrupdata["general info"] = generalinfos
                altgrupdata["image gallery"] = imagegallerylist
                altgrupdata["alt-grup id"] = {}
        
                modeldata["technical info"] = technicalinfos
                modeldata["technical images"] = technicalimages
                
                #urunlere giriliyor
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,'multiselect__tag-icon')))
                while True:
                    try:
                        buttons = driver.find_elements(By.CLASS_NAME, 'multiselect__tag-icon')
                        if len(buttons) <= 0:
                            sleep(1)
                            break
                        else:
                            buttons[-1].click()             ## filtreleri kaldir
                            
                    except Exception as e:
                        print(e)
                        print("secimler silinirken hata olustu")
                        sleep(1)    
                
                grupurl = driver.current_url
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.pt-6 tbody.divide-y > tr")))
                linkuzantilari = []
                cogul = False
                counter = 0
                while True:
                    try:
                        anlik_sayfa = driver.find_elements(By.CSS_SELECTOR, "table.bega-table")
                        if len(anlik_sayfa) == 1:
                            html = anlik_sayfa[0].get_attribute("outerHTML")
                            soup_2 = bs(html, "lxml")
                            soup_2 = soup_2.find_all('tr', attrs={'class': 'relative cursor-pointer'})
                            for link in soup_2:
                                link2 = link.find('th').text
                                link2 = link2.replace(" ", "")
                                
                                linkuzantilari.append(link2)

                        elif len(anlik_sayfa) > 1:
                            cogul = True
                            for urunblogu in anlik_sayfa:    
                                html = urunblogu.get_attribute("outerHTML")
                                soup_2 = bs(html, "lxml")
                                soup_2 = soup_2.find_all('tr', attrs={'class': 'relative cursor-pointer'})
                                for link in soup_2:
                                    link2 = link.find('th').text
                                    link2 = link2.replace(" ", "")
                                    
                                    linkuzantilari.append(link2)


                        urunlinki = driver.current_url
                        urunlinkitemp = urunlinki
                        break
                    
                    except:
                        sleep(counter**2)
                        counter += 1
                        if counter == 5:
                            print("urunun info pageine girilemedi")
                            tofile(jsonlist)
                            break

                degisken = '&'
                
                for index in range(1): # len(linkuzantilari)
                    urunlinki = urunlinkitemp
                    try:
                        urunlinki = urunlinki + f"{degisken}product={linkuzantilari[index]}&tab=info"
                        driver.get(urunlinki)
                        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR,"nav.mb-0"))) 
                        
                    except:
                        urunlinki = urunlinkitemp
                        degisken = '?'
                        urunlinki = urunlinki + f"{degisken}product={linkuzantilari[index]}&tab=info"
                        driver.get(urunlinki)
                        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR,"nav.mb-0"))) 
                    finally:
                        sleep(2)
                
                    
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"span.font-semibold")))
               
                    model["urunler"][linkuzantilari[index]] = {}
                    urun = model["urunler"][linkuzantilari[index]]
                    
                    try:
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.app-wrap div.h-full > picture > img")))
                        urunfotosu = driver.find_element(By.CSS_SELECTOR, "div.app-wrap div.h-full > picture > img").get_attribute("data-src")
                        urun["urun fotosu"] = urunfotosu
                    except:
                        print("urun fotosu alinamadi")
                        urun["urun fotosu"] = "urun fotosu alinamadi"


                    alldivs = driver.find_elements(By.CSS_SELECTOR, "div.mb-4 div.pb-6")
                    for div in alldivs:
                        subinfo = div.find_element(By.CSS_SELECTOR, "h5 > span").text.strip()
                        urun[subinfo] = {}
                        urunbilgibaslik = urun[subinfo]
                        diva = div.find_elements(By.CSS_SELECTOR, "div.po__list")
                        
                        for subdiv in diva:
                            subtitle = subdiv.find_element(By.CSS_SELECTOR, "div > div").text.split("\n")[0].strip()
                            try:
                                subvalue = subdiv.find_element(By.CSS_SELECTOR, 'div > div.font-semibold').text.strip()
                            except:
                                subvalue = subdiv.find_element(By.CSS_SELECTOR, 'span.multiselect__single').text.strip()
                            finally:
                                urunbilgibaslik[subtitle] = subvalue

                    

                    counter4 = 0
                    while True:
                        try:  
                            currenturl = driver.current_url
                            currenturl = currenturl.replace("info", "download")
                            driver.get(currenturl)

                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.mb-5 li.po__list')))
                            soup3 = bs(driver.find_element(By.CSS_SELECTOR,'body').get_property('outerHTML'), 'lxml')
                            alldivs = soup3.find('div', attrs={'class': 'mb-5'})
                            title2 = alldivs.find('h5').text.replace("\n","")
                            title2 = title2.strip()
                            liobjects = alldivs.find_all('li', attrs={'class': 'po__list po__list-border'})
                            downlinklist = []
                            for li in liobjects:
                                downlink = li.find('a')['href']
                                downlinklist.append(downlink)
                            try:
                                ekstralinkler = alldivs.find_all('span', attrs={'class': 'po__download-span'})
                                for extra in ekstralinkler:
                                    downlink = extra.find('a')['href']
                                    if "dial" not in downlink:
                                        downlinklist.append(downlink)
                            except:
                                pass
                            urun.update({"Download Links": downlinklist})
                            break
                        except Exception as e:
                            #print(e)
                            if counter4 == 3:
                                print("download linkleri alinamadi")
                                tofile(jsonlist)
                            sleep(counter4**2)
                            counter4 += 1
                    #### ACCESSORIES ####
                    
        
                    try:
                        accessories = {}
                        currenturl = driver.current_url
                        currenturl = currenturl.replace("download", "supplements")
                        driver.get(currenturl)
                        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h5.mb-1')))
                        soup = bs(driver.find_element(By.CSS_SELECTOR,'body').get_property('outerHTML'), 'lxml')
                        alldivs = soup.select('div.tab-content div.po__supplementary-group')
                        for div in alldivs:
                            accessoryname = div.select_one('h5.mb-1 > span').text.strip()
                            accessories[accessoryname] = {}
                            accessory = accessories[accessoryname]
                            accessory["accessory link"] = div.select_one('a')['href']
                            accessory["accessory image"] = div.select_one('a picture img')['src']
                            
                            downloads = []
                            temp = div.select('div.po__list-item-content-download > a')
                            for t in temp:
                                downloads.append(t['href'])
                                
                            accessory["downloads"] = downloads
                            urun["accessories"] = {}
                            urun["accessories"] = accessories
                        
                    except:
                        print("urunun accessories pagei yok")
                
                driver.get(serilink)
        driver.get(mainurl)     

tofile(jsonlist)
pass
driver.quit()