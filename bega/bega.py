import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from time import sleep
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import requests



options = webdriver.ChromeOptions()
options.add_extension("cookies.crx")
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=options)
driver.maximize_window()
url = "https://www.bega.com/en/products/"

jsonlist = {}

def tofile(jsonlist):
    with open("bega.json", "w", encoding="utf-8"):
        json.dump(jsonlist, open("bega.json", "w", encoding="utf-8"), indent=4, ensure_ascii=False)


kategoriler_list = []
driver.get(url)
sleep(1)


elements = driver.find_elements(By.CLASS_NAME, 'relative.overflow-hidden.rounded.group.hover-zoom.z-0.bg-gray-darker')


for i in range(1):  # Change 2 to len(elements) to get all categories
    elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'relative.overflow-hidden.rounded.group.hover-zoom.z-0.bg-gray-darker'))
    )
    kategoriler_list.append(elements[i].text)
    elements[i].click()
    #print("entered sub category: " + kategoriler_list[i])
    jsonlist.update({kategoriler_list[i]: {}})

    sleep(1)  # You may need to adjust the sleep duration based on your page's loading time

    # kategori sub basliklari cekiliyor.
    soup = bs(driver.page_source, 'lxml')
    subbasliklar = soup.find_all('h5', attrs={'class': 'font-semibold'})

    for k in range(2,3):  # Change 2 to len(subbasliklar) to get all sub categories
        counter = 0
        while True:
            try:
                soup = bs(driver.page_source, 'lxml')
                subbasliklar = soup.find_all('h5', attrs={'class': 'font-semibold'})
                jsonlist[kategoriler_list[i]].update({subbasliklar[k].text: {}})
                break
            except:
                sleep(counter**2)
                counter += 1
                if counter == 5:
                    print("subbaslik alinamadi")
                    tofile(jsonlist)
                    break

        urunlerList = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'bg-gray-medium.aspect-h-1.aspect-w-1.rounded.relative.group.shadow-light'))
        )

        for u in range(24,26):  # Change 2 to len(urunlerList) to get all products
            subbasliklarurl = driver.current_url
            sleep(1)
            urunlerList = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'bg-gray-medium.aspect-h-1.aspect-w-1.rounded.relative.group.shadow-light'))
            )
            urunlerList[u].click()
            #print("entered product")
            
            generalinfolist = []
            technicalinfolist = []
            counter2 = 0
            while True:
                try:
                    soup = bs(driver.page_source, 'lxml')
                    infos = soup.find_all('div', attrs={'class': 'max-w-60ch md:max-w-75ch'})

                    generalinfo = infos[5].find_all('p')
                    technicalinfo = infos[6].find_all('p')

                    
                    break
                except:
                    # sleep 2^counter seconds
                    sleep(2**counter2)
                    counter2 += 1
                    if counter2 == 5:
                        print("urun soupu alinamadi")
                        tofile(jsonlist)
                        break
                        
            
            # Merging general info
            for g in generalinfo:
                generalinfolist.extend(g.text.split(" \n"))



            

            # Merging technical info
            for t in technicalinfo:
                if t.text.strip() != "":
                    technicalinfolist.extend(t.text.split(" \n"))
            

            techimg1 = soup.find('div', attrs={'class': 'h-full relative pb-8'})
            techimg1 = techimg1.find('source').get('data-srcset')
            pass
            
            techimg2 = soup.find('div', attrs={'class': 'mb-8 w-46 h-46 sm:w-auto sm:h-auto rounded bg-gray-medium shadow-light cursor-pointer block relative mx-auto sm:mx-0 hidden sm:block'})
            techimg2 = techimg2.find('source').get('data-srcset')
            
            
            
            
            imagegallery = soup.find_all('div', attrs={'class': 'mb-4 bg-transparent text-primary'})
            imagegallerylist = []
            for img in imagegallery:
                imgurl = img.find('source').get('data-srcset')
                imagegallerylist.append(imgurl)
            
            
            
            #deselect filters
            
            
            while True:
                buttons = driver.find_elements(By.CLASS_NAME, 'multiselect__tag-icon')
                if len(buttons) <= 0:
                    break
                else:
                    buttons[-1].click()
            
            linkuzantilari = []
            cogul = False
            counter3 = 0
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
                    sleep(counter3**2)
                    counter += 1
                    if counter == 5:
                        print("urunun info pageine girilemedi")
                        tofile(jsonlist)
                        break
    
            for index in range(2): # len(linkuzantilari)
                urunlinki = urunlinkitemp
                sleep(3)
                try:
                    if not cogul:
                        urunlinki = urunlinki + f"&product={linkuzantilari[index]}&tab=info"
                    elif cogul:
                        urunlinki = urunlinki + f"?product={linkuzantilari[index]}&tab=info"
                except Exception as e:
                    print(e)
                    print("urun linki alamadim :(((")    
                # print(index , " inci " , urunlinki , "\n")
                driver.get(urunlinki)
                sleep(1)
                counter6 = 0
                while True:
                    try:
                        if index == 0:
                            jsonlist[kategoriler_list[i]][subbasliklar[k].text].update({"urun_grubu" : {}})
                            jsonlist[kategoriler_list[i]][subbasliklar[k].text]["urun_grubu"].update({"kod" : linkuzantilari[0]})
                            jsonlist[kategoriler_list[i]][subbasliklar[k].text]["urun_grubu"].update({"General Info": generalinfolist})
                            jsonlist[kategoriler_list[i]][subbasliklar[k].text]["urun_grubu"].update({"Technical Data": {}})
                            jsonlist[kategoriler_list[i]][subbasliklar[k].text]["urun_grubu"]["Technical Data"].update({"Technical Info": technicalinfolist})
                            jsonlist[kategoriler_list[i]][subbasliklar[k].text]["urun_grubu"]["Technical Data"].update({"Images": [techimg1, techimg2]})
                            jsonlist[kategoriler_list[i]][subbasliklar[k].text]["urun_grubu"].update({"Image Gallery": imagegallerylist}) 
                        jsonlist[kategoriler_list[i]][subbasliklar[k].text]["urun_grubu"].update({linkuzantilari[index] : {}}) 
                             
                            
                        counternested = 0
                        while True:
                            try:        
                                soup = bs(driver.page_source, 'lxml')
                                alldivs = soup.find_all('div', attrs={'class': 'pb-6'})
                                currenturl = driver.current_url
                                imgfind = soup.find('div', attrs={'class' : 'h-full w-full'}).find('img').get('data-src')
                                jsonlist[kategoriler_list[i]][subbasliklar[k].text]["urun_grubu"][linkuzantilari[index]].update({"Urun Image": imgfind})
                                jsonlist[kategoriler_list[i]][subbasliklar[k].text]["urun_grubu"][linkuzantilari[index]].update({"Urun Linki": currenturl})
                                break
                            except Exception as e:
                                print(e)
                                sleep(2**counternested)
                                counternested += 1
                                if counternested == 5:
                                    print("urun img alinamadi")
                                    tofile(jsonlist)
                                    break
                                
                        break
                    except:
                        sleep(counter6**2)
                        counter6 += 1
                        if counter6 == 5:
                            print("urunun info pageine girilemedi")
                            tofile(jsonlist)
                            break
                
                
                
                
                
                
                counter = 0
                for div in alldivs:
                    
                    if counter < 5:
                        counter += 1
                        continue
                    
                    title = div.find('h5').text
                    jsonlist[kategoriler_list[i]][subbasliklar[k].text]["urun_grubu"][linkuzantilari[index]].update({title: {}})
                    # jsonlist[kategoriler_list[i]][subbasliklar[k].text][linkuzantilari[index]][title]
                    allsubdivs = div.find_all('div', attrs={'class': 'po__list po__list-border'})
                    
                    for subdiv in allsubdivs:
                        
                        subtitle = subdiv.find('div', attrs={'class': 'po__list-entry'}).find('div').text
                        try:
                            subvalue = subdiv.find('span', attrs={'class': 'multiselect__single'}).text
                        except:
                            subvalue = subdiv.find('div', attrs={'class': 'font-semibold'}).text
                        finally:
                            jsonlist[kategoriler_list[i]][subbasliklar[k].text]["urun_grubu"][linkuzantilari[index]][title].update({subtitle: subvalue})
            

                counter4 = 0
                while True:
                    try:  
                        currenturl = driver.current_url
                        currenturl = currenturl.replace("info", "download")
                        driver.get(currenturl)
                        sleep(1)
                        soup3 = bs(driver.page_source, 'lxml')
                        alldivs = soup3.find('div', attrs={'class': 'mb-5'})
                        title2 = alldivs.find('h5').text.replace("\n","")
                        title2 = title2.strip()
                        jsonlist[kategoriler_list[i]][subbasliklar[k].text]["urun_grubu"][linkuzantilari[index]].update({title2: {}})
                        liobjects = alldivs.find_all('li', attrs={'class': 'po__list po__list-border'})
                        downlinklist = []
                        for li in liobjects:
                            downlink = li.find('a')['href']
                            downlinklist.append(downlink)
                        jsonlist[kategoriler_list[i]][subbasliklar[k].text]["urun_grubu"][linkuzantilari[index]][title2].update({"Download Links": downlinklist})
                        break
                    except:
                        sleep(counter4**2)
                        counter4 += 1
                        if counter4 == 5:
                            print("download linkleri alinamadi")
                            tofile(jsonlist)
                
                accessories = {}
                
                while True:
                    try:
                        currenturl = driver.current_url
                        currenturl = currenturl.replace("download","supplements")
                        driver.get(currenturl)
                        sleep(1)
                        soup4 = bs(driver.page_source, 'lxml')
                        alltitles = soup4.find_all('h5', attrs={'class': 'mb-1'})
                        alldivs = soup4.find_all('div', attrs={'class' : 'po__list-border-first'})
                        for titleindex in range(len(alltitles)):
                            accessories.update({alltitles[titleindex].text : {}})
                            for divindex in range(len(alldivs)):
                                allsubdivs = alldivs[divindex].find_all('div', {'class': 'po__list-item po__list po__list-border xl:flex'})
                                for subdiv in allsubdivs:
                                    aksesuaradi = soup4.select("#po-app > div.app-wrap.md\:grid.md\:grid-cols-2.rounded > div.w-full.px-4.md\:px-6.xl\:px-15.bg-white > div > div.po-nav-tabs-wrap.relative.md\:h-screen > div.tab-content.md\:h-full > div > div > div > div:nth-child(1) > div > div.po__list-item-content-top.ml-0.xl\:ml-26 > div:nth-child(1) > div:nth-child(1) > a > span > span").text
                                    accessories[alltitles[titleindex].text].update({"aksesuar adi": aksesuaradi})
                                    accessories[alltitles[titleindex].text].update({"aksesuar linki": subdiv.find('a').get('href')})    
                                    indirmelinkleri = subdiv.find_all('div', {'class': 'po__list-item-content-download'})
                                    linkler = []
                                    for indirmelinki in indirmelinkleri:
                                        linkler.append(indirmelinki.find('a').get('href'))
                                    accessories[alltitles[titleindex].text].update({"indirme linkleri": linkler})
                        jsonlist[kategoriler_list[i]][subbasliklar[k].text]["urun_grubu"][linkuzantilari[index]].update({"aksesuarlar": accessories})
                        break
                    except:
                        print("tabi ki calismadi")
                        sleep(3)
                        
                
                        
                
                
            ## aksesuar adi alinmadi
            ## sadece bir aksesuarin linki geldi
            
            driver.get(subbasliklarurl)
            sleep(2)


    driver.get(url)
    sleep(1)
    






tofile(jsonlist)

print("\nexitting...")
driver.quit()