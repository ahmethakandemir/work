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
mainurl = "https://dcw-editions.fr/en/collections"
photoUrlBeginning = "https://dcw-editions.fr"
#write a function to write the errors to the log.txt file we will append to it every error
jsondata = {}

log = open('log.txt','a')



def tofile(jsondata):
    with open('data.json', 'w') as outfile:
        json.dump(jsondata, outfile, indent=2)


driver.get(mainurl)


webdriverwait = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.dcw-card')))
soup = bs(driver.find_element(By.CSS_SELECTOR,'body').get_property('outerHTML'), 'lxml')
familydivs = soup.select_one('div.thumbs-list')
familydivs = familydivs.select('div.dcw-card')
# limit familydivs to 2
familydivs = familydivs[1:3]
 
i = 0
for familydiv in familydivs:
    webdriverwait = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.dcw-card')))
    soup = bs(driver.find_element(By.CSS_SELECTOR,'body').get_property('outerHTML'), 'lxml')
    
    family_name = familydiv.select_one('h1.collection').text.strip()
    family_designer = familydiv.select_one('div.name').text.strip()
    family_img_mainpage = photoUrlBeginning + familydiv.select_one('img')['src']
    
    jsondata[family_name] = family = {}
    family['aile_data'] = aile_data = {'family_name': family_name, 'collection_designer': family_designer, 'collection_image': family_img_mainpage}
    
    webdriverwait = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.dcw-card h1.collection')))
    counter = 0
    while counter < 5:    
        try:
            element = driver.find_elements(By.CSS_SELECTOR, 'div.dcw-card')[i]
            driver.execute_script("arguments[0].click();", element)# click on the family
            
            webdriverwait = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.dcw-card')))
            innersoup = bs(driver.find_element(By.CSS_SELECTOR,'body').get_property('outerHTML'), 'lxml')
            
            family_img_inner = photoUrlBeginning + innersoup.select_one('div.collection div.wrapper div.image img')['src']
            family_info_text = innersoup.select_one('div.collection div.wrapper div.text div.titre').text.strip() + '--' + innersoup.select_one('div.collection div.wrapper div.text div.texte').text.strip()
            family_info_text = family_info_text.split('\n','--')
            family_info_text = list(filter(None, family_info_text))
            aile_data['inner_collection_image'] = family_img_inner
            aile_data['collection_info'] = family_info_text
            break
        except:
            counter += 1
            if counter == 5:
                log.write(family_name + ' --> ' + 'ERROR' + '\n')

            pass
    
    aileurl = driver.current_url
    aile_data['aile_url'] = aileurl
    products = driver.find_elements(By.CSS_SELECTOR, 'div.thumbs-list div.dcw-card')
    
    g = 0
    for product in products:
        counter = 0
        while counter < 5:
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.thumbs-list div.dcw-card div.title')))
                soup = bs(driver.find_element(By.CSS_SELECTOR,'body').get_property('outerHTML'), 'lxml')
                product_name = soup.select('div.title')[g].text.strip()
                product_img = soup.select('img')[g]['src']
                if product_img[0] == '/':
                    product_img = photoUrlBeginning + product_img
                
                element = driver.find_elements(By.CSS_SELECTOR, 'div.title')[g]
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
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'img')))
                soup = bs(driver.find_element(By.CSS_SELECTOR,'body').get_property('outerHTML'), 'lxml')
                product_images = soup.select('div.swiper-slide:not(.swiper-slide-duplicate)')
                images = []
                for index in range(len(product_images)):
                    images.append(photoUrlBeginning + product_images[index].select_one('img')['src'])
                break
            
            except Exception as e:
                counter += 1
                if(counter == 5):
                    print(e)
                    print('error in images')
                    print(f"aile: {i},grup: {g}")
                    log.write(family_name + ' --> ' + product_name + ' --> ' + 'ERROR' + '\n')

                pass
        
        
        
        print(len(images))
        
        
        
        
        
        
        
        
        g += 1
        driver.get(aileurl)
    
    
    
    
    
    i += 1
    driver.get(mainurl)

tofile(jsondata)
log.close()
    
    