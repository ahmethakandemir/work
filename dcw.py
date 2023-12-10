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
jsondata = {}
open('log.txt','w',).close()
log = open('log.txt','a', encoding="utf-8")



def tofile(jsondata):
    with open('data.json', 'w', encoding="utf-8") as outfile:
        json.dump(jsondata, outfile, indent=2, ensure_ascii=False)


driver.get(mainurl)


webdriverwait = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.dcw-card')))
soup = bs(driver.find_element(By.CSS_SELECTOR,'body').get_property('outerHTML'), 'lxml')
familydivs = soup.select_one('div.thumbs-list')
familydivs = familydivs.select('div.dcw-card')
# limit familydivs to 2
id = 700000
i = 0
for familydiv in familydivs:
    familyid = id + (i * 40)
    webdriverwait = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.dcw-card')))
    soup = bs(driver.find_element(By.CSS_SELECTOR,'body').get_property('outerHTML'), 'lxml')
    
    family_name = familydiv.select_one('h1.collection').text.strip()
    aynimi = False
    ayniindex = 0
    for index in aileler.aileler_ayni:
        if index in family_name:
            # family_name = index
            ayniindex = index
            anyimi = True
            break
    
    family_designer = familydiv.select_one('div.name').text.strip()
    family_img_mainpage = photoUrlBeginning + familydiv.select_one('img')['src']
    
    jsondata[family_name] = family = {}
    family['aile_data'] = aile_data = {'family_id': 0,'family_name': family_name, 'family_designer': family_designer, 'family_image': family_img_mainpage}
    
    webdriverwait = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.dcw-card h1.collection')))
    tempurl = driver.current_url
    counter = 0
    while counter < 5:    
        try:
            element = driver.find_elements(By.CSS_SELECTOR, 'div.dcw-card')[i]
            driver.execute_script("arguments[0].click();", element)# click on the family
            
            webdriverwait = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.dcw-card')))
            innersoup = bs(driver.find_element(By.CSS_SELECTOR,'body').get_property('outerHTML'), 'lxml')
            
            family_img_inner = photoUrlBeginning + innersoup.select_one('div.collection div.wrapper div.image img')['src']
            family_info_text = innersoup.select_one('div.collection div.wrapper div.text div.titre').text.strip().replace('\n','. ') + innersoup.select_one('div.collection div.wrapper div.text div.texte').text.strip().replace('\n',' ')
            aile_data['family_info'] = family_info_text
            break
        except:
            driver.get(tempurl)
            counter += 1
            if counter == 5:
                log.write(family_name + ' --> ' + 'ERROR' + '\n')

            pass
    
    aileurl = driver.current_url
    aile_data['family_id'] = familyid
    aile_data['family_link'] = aileurl
    
    seriid = str(familyid) + '-1'
    
    family["seriler"] = seriler = {}
    
    if aynimi:
        seriid = str(familyid) + '-2'
        family["seriler"] = seriler = {} #################################################################################
        
    
    
    seriler[family_name] = seri = {}
    seri["series_data"] = seri_data = {}
    seri_data['series_id'] = seriid
    seri_data['series_name'] = family_name
    seri_data['series_img'] = family_img_inner
    seri_data['series_link'] = aileurl
    
    seri["gruplar"] = gruplar = {}
    
    
    products = driver.find_elements(By.CSS_SELECTOR, 'div.thumbs-list div.dcw-card')
    
    g = 0
    for product in products:
        productdict = {}
        counter = 0
        while counter < 5:
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.thumbs-list div.dcw-card div.title')))
                soup = bs(driver.find_element(By.CSS_SELECTOR,'body').get_property('outerHTML'), 'lxml')
                product_name = soup.select('div.thumbs-list div.title')[g].text.strip()
                product_img = soup.select('div.thumbs-list img')[g]['src']
                if product_img[0] == '/':
                    product_img = photoUrlBeginning + product_img
                
                element = driver.find_elements(By.CSS_SELECTOR, 'div.thumbs-list div.title')[g]
                
                gruplar[product_name] = grup = {}
                grup['grup_data'] = grup_data = {}
                
                grupid = seriid + '-' + chr(g + 65)
                grup_data['group_id'] = grupid
                
                grup_data['group_name'] = product_name
                grup_data['group_img'] = product_img
                grup_data['group_link'] = ''
                grup['ürünler'] = urunler = []
                
                
                driver.execute_script("arguments[0].click();", element)# click on the family
                # print(product_name , " --> ", product_img)
                break
            except Exception as e:
                print(e)
                counter += 1
                if(counter == 5):
                    log.write(family_name + ' --> ' + product_name + ' --> ' + 'ERROR' + '\n')
                pass
        counter = 0
        while counter < 5:
            try:
                grup_data['group_link'] = driver.current_url
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'img')))
                soup = bs(driver.find_element(By.CSS_SELECTOR,'body').get_property('outerHTML'), 'lxml')
                product_images = soup.select('div.swiper-slide:not(.swiper-slide-duplicate)')
                images = []
                video_link = []
                for index in product_images:
                    try:
                        try:
                            images.append(photoUrlBeginning + index.select_one('img')['src'])
                        except:
                            images.append(photoUrlBeginning + index.select_one('img')['data-src'])
                    except:
                        video_link.append(index.select_one('iframe')['src'])
                
                productdict['product_name'] = product_name
                productdict['product_id'] = grup_data['group_id'] + '-1'
                productdict['product_img'] = product_img
                productdict['images'] = images
                if len(video_link) > 0:
                    productdict['video_link'] = str(video_link[0])
                
                # print('------------------')
                break
            
            except Exception as e:
                counter += 1
                if(counter == 5):
                    print(e)
                    errorlocation = f"error in images of aile: {i},grup: {g}"
                    log.write(errorlocation + '\n')

                pass
        
        description = soup.select_one('div.container div.infos div.usages > div.content').text.strip().replace('\n',' ')
        
        tech_infosdiv = soup.select('div.container div.infos div.technical-infos > div.content > div.technical-infos-bloc')
        tech_infoslist = {}
        
        for index in tech_infosdiv:
            tech_infoslist[index.select_one('div.technical-infos-titre').text.strip()] = index.select_one('div.technical-infos-content').text.strip().replace('\n',' ')
            try:
                tech_infoslist['ip_class_img'] = photoUrlBeginning + index.select_one('div.technical-infos-content > img')['src']
            except:
                pass
        downloadsdivs = soup.select('div.container div.infos div.downloads > div.content > div.document > a')
        downloads = {}
        
        for index in downloadsdivs:
            downloads[index.text.strip()] = photoUrlBeginning + index['href']
            
        
        tech_schema = photoUrlBeginning + soup.select_one('div.container div.infos div.technical-schema > div.content > img')['src']

        productdict['description'] = description
        productdict['tech_infos'] = tech_infoslist
        productdict['downloads'] = downloads
        productdict['tech_schema'] = tech_schema
        
        try:
            divs = soup.select_one('div.configurateur div.color')
            colors = {}
            for div in divs:
                colors[div.select_one('div.name').text.strip()] = photoUrlBeginning + div.select_one('div.image img')['src']
        except:
            pass
        
        productdict['different_color_images'] = colors
        
        
        
        urunler.append(productdict)
        
        # print(len(images))
        
        
        
        
        
        
        
        
        g += 1
        driver.get(aileurl)
    
    
    
    
    
    i += 1
    driver.get(mainurl)

driver.quit()

tofile(jsondata)
log.close()
    