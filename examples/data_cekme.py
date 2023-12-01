import json
import requests
from time import sleep
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from aileler import aileler_esleme


def aile_seri_adlandırma(aile_adı):
    seri_adı = aile_adı
    if aile_adı in aileler_esleme["aynı_kalanlar"]:
        seri_adı = aile_adı
    else:
        for yeni_aile in aileler_esleme["yeni_aileler"]:
            if aile_adı.startswith(yeni_aile):
                seri_adı = aile_adı
                aile_adı = yeni_aile
                break
    return aile_adı, seri_adı


def özellik_getir(ürün_linki):
    ürün_özellikleri = {}
    ürün_özellikleri["series_link"] = aile_linki
    ürün_özellikleri["group_link"] = grup_linki
    ürün_özellikleri["product_link"] = ürün_linki
    ürün_özellikleri["product_type"] = aile_ürün_tipi

    deneme_sayacı = 0
    is_succeeded = False
    while deneme_sayacı < 5:
        try:
            ürün_sayfası = bs(requests.get(ürün_linki).text, "lxml")
            ürün_özellikleri["ürün_adı"] = ürün_sayfası.find(
                class_="mb-8 text-xl leading-lgxl md:text-h4 md:leading-h4"
            ).text.replace("New", "").strip()
            is_succeeded = True
            break
        except:
            pass
    if not is_succeeded:
        raise Exception("Ürün sayfası açılmadı")

    bulunan_dosyalar = []
    # Technical ve polar diagram image çekme
    for img_box in ürün_sayfası.find_all(
        class_="pt-20 md:pt-32 pb-20 md:pb-30 w-full md:w-3/4"
    ):
        box_title = img_box.find("h5").text
        if "Technical" in box_title:
            ürün_özellikleri["technical_images"] = [img_box.find("img")["src"]]
        elif "Schematic" in box_title:
            ürün_özellikleri["polar_images"] = [img_box.find("img")["src"]]

    try:
        spare = ürün_sayfası.find(class_="container-fluid pt-20 md:pt-32 pb-32 md:pb-46")
        box_title = spare.h4.text
        if "Spare" in box_title:
            ürün_özellikleri["spare_images"] = [a["src"] for a in spare.find_all("img")]
    except:
        pass
    try:
        ürün_özellikleri["ürün_açıklaması"] = ürün_sayfası.find(
            class_="subtitle-02 mb-20 md:mb-24 text-gray-500"
        ).text.replace("Read more", "").strip()
        ürün_özellikleri["ürün_açıklaması_kısa"] = ürün_özellikleri["ürün_açıklaması"].split(".")[0]
    except:
        pass
    try:
        ürün_özellikleri["technical_summary"] = ürün_sayfası.find(
            class_="subtitle-02 mt-6 mb-20 font-bold"
        ).text.strip()
    except:
        pass
    try:
        ürün_özellikleri["surface_images"] = [
            ürün_sayfası.find(class_="w-full md:col-5/12 md:order-2")
            .find("picture")
            .source["srcset"]
            .split(",")[1]
            .split("jpg")[0]
            + "jpg"
        ]
    except:
        pass
    try:
        ürün_özellikleri["awards"] = []
        for award_soup in ürün_sayfası.find_all(class_="mb-4 last:mb-0"):
            award = {}
            award["src"] = award_soup.img["src"]
            award["name"] = award_soup.img["alt"]
            ürün_özellikleri["awards"].append(award)
    except:
        pass

    ürün_özellikleri["ürün_kodu"] = ürün_sayfası.find(class_="subtitle-01 mr-6 md:mr-4").text.strip()
    try:
        ürün_özellikleri["ürün_rengi"] = ürün_sayfası.find(class_="subtitle-01 mr-6 md:mr-4").find_next_sibling().text.strip()
    except:
        pass
    try:
        ürün_özellikleri["Designer"] = ürün_sayfası.find(class_="hidden md:block md:text-xl md:leading-h5 md:mb-20").text.replace("Designed by ", "").strip()
    except:
        pass
    tablolar = ürün_sayfası.find_all(class_="pt-20 md:pt-32 pb-20 md:pb-30")
    for tablo in tablolar:
        tablo_başlığı = tablo.h5.text.strip()
        if "rawing" in tablo_başlığı:
            ürün_özellikleri[f"{tablo_başlığı}"] = tablo.find("img")["src"]
        else:
            özellik_tablosu = tablo.select(".specs-container > div")
            for özellik in özellik_tablosu:
                try:
                    özellik_satırı = özellik.select(".row > div")
                    ürün_özellikleri[f"{özellik_satırı[0].text.strip()}"] = özellik_satırı[1].text.strip()
                except:
                    pass
    try:
        ürün_özellikleri["Sertifikalar"] = []
        for sertifika in ürün_sayfası.find_all(class_="w-16 h-16 mb-4"):
            sertifika_ = {}
            sertifika_["name"] = sertifika["alt"].replace(" Certified", "")
            sertifika_["src"] = sertifika["src"]
            ürün_özellikleri["Sertifikalar"].append(sertifika_)
    except:
        pass
    try:
        ürün_özellikleri["Aksesuarlar"] = [
            aksesuar.find(class_="accessory-name line-clamp-2").text.strip()
            + " "
            + aksesuar.find(class_="accessory-code").text.strip()
            for aksesuar in ürün_sayfası.find_all(class_="accessory-card-container")
        ]
    except:
        pass
    indirmeler = ürün_sayfası.find_all(class_="my-4")
    ldt_ies = []
    for indirme in indirmeler:
        try:
            if "urlVideo1" in indirme.div["id"]:
                ürün_özellikleri["video"] = "var"
                continue
        except:
            pass
        try:
            indirme_linki = indirme.a["href"]
            dosya_türü = indirme.a.find(class_="inline-block mr-16").text.strip()
            if dosya_türü == "LDT / IES":
                ldt_ies.append(indirme_linki)
            else:
                bulunan_dosyalar.append(dosya_türü)
                ürün_özellikleri[dosya_türü] = indirme_linki
        except:
            try:
                indirme_linki = indirme["href"]
            except:
                ürün_özellikleri[dosya_türü] = "link_yok"
                continue
            dosya_türü = indirme.find(class_="inline-block mr-16").text.strip()
            if dosya_türü == "LDT / IES":
                ldt_ies.append(indirme_linki)
            else:
                if dosya_türü in bulunan_dosyalar:
                    if isinstance(ürün_özellikleri[dosya_türü], list):
                        ürün_özellikleri[dosya_türü].append(indirme_linki)
                    else:
                        pre_doc = ürün_özellikleri[dosya_türü]
                        ürün_özellikleri[dosya_türü] = []
                        ürün_özellikleri[dosya_türü].append(pre_doc)
                        ürün_özellikleri[dosya_türü].append(indirme_linki)
                else:
                    bulunan_dosyalar.append(dosya_türü)
                    ürün_özellikleri[dosya_türü] = indirme_linki
        ürün_özellikleri["LDT / IES"] = ldt_ies

    return ürün_özellikleri


urunler_json = {}
ana_link = "https://professional.flos.com"
decorative_aileler_link = "https://professional.flos.com/en/global/catalogs/decorative/?page=100"

options = webdriver.ChromeOptions()
options.add_extension("./cookies.crx")
driver = webdriver.Chrome(options=options)
driver.get(decorative_aileler_link)
driver.maximize_window()
sleep(5)

aileler_container_html = driver.find_element(By.CLASS_NAME, "container-full").get_attribute("innerHTML")
soup = bs(aileler_container_html, "lxml")
aileler = soup.find_all(class_="_col col-1/1 md:col-3/9 mb-26 md:mb-32")
aile_number = 0
id_sayac = 775002
harfler = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
for aile in aileler:
    aile_number += 1
    aile_linki = ana_link + aile.div.a["href"]
    aile_ürün_tipi = aile.select_one(".text-container span.overline").text.strip()
    aile_görseli = aile.select_one(".image-container img")["src"]
    aile_adı = aile.select_one(".text-container .link-text").text.strip()

    aile_adı, seri_adı = aile_seri_adlandırma(aile_adı)
    aile_data = urunler_json.get(aile_adı, {
        "aile_data": {"family_id": str(id_sayac + (len(urunler_json) * 40))},
        "seriler": {}
    })
    family_id = aile_data["aile_data"]["family_id"]
    seri_id = f"{family_id}-{str(len(aile_data['seriler']) + 1)}"
    seri_data = {
        "seri_data": {
            "series_id": seri_id,
            "series_name": seri_adı,
            "series_product_type": aile_ürün_tipi,
            "series_link": aile_linki,
            "application_image": aile_görseli
        },
        "gruplar": {}
    }
    aile_data["seriler"][seri_adı] = seri_data
    urunler_json[aile_adı] = aile_data

    if "/model/" in aile_linki:
        grup_linki = aile_linki
        grup_adı = seri_adı
        grup_id = f"{seri_id}-{harfler[len(seri_data['gruplar'])]}"
        grup_data = {
            "grup_data": {
                "group_id": grup_id,
                "group_name": grup_adı,
                "group_link": grup_linki
            },
            "ürünler": []
        }
        seri_data["gruplar"][grup_adı] = grup_data

        while True:
            try:
                grup_sitesi = bs(requests.get(grup_linki).text, "lxml")
                grup_adı = grup_sitesi.select_one(r".text-h4.leading-h4.md\:text-h3.md\:leading-h3").text.strip()
                break
            except:
                pass

        grup_görselleri = [i["src"] for i in grup_sitesi.select(".main-swiper.swiper-container .swiper-slide img")]
        if len(grup_görselleri):
            grup_data["grup_data"]["group_image"] = grup_görselleri[0]
            grup_data["grup_data"]["application_images"] = grup_görselleri[1:]

        alt_gruplar_container = grup_sitesi.find_all(class_="items-card-container h-full")
        if len(alt_gruplar_container) == 0:
            if len(grup_sitesi.find_all(class_="inline-block mr-4")) != 0:
                while True:
                    try:
                        driver.get(grup_linki)
                        değişkenler = driver.find_elements(By.CLASS_NAME, "inline-block mr-4")
                        break
                    except:
                        pass
                if len(değişkenler) == 0:
                    try:
                        değişkenler = driver.find_elements(By.XPATH, '//*[@id="el-PLINE1"]/div[1]/div[2]/div[2]/div/div[1]/div/div/span')
                    except:
                        pass
                for değişken in değişkenler:
                    try:
                        değişken.click()
                    except:
                        driver.find_element(By.XPATH, '//*[@id="MenuSite"]/div/div/div[2]/div[1]/div[1]/span').click()
                        sleep(1)
                        driver.find_element(By.CSS_SELECTOR, '#MenuSite > div.container-fluid.default.\!bg-white > div > div.col-12\/12._col.flex.flew-row.items-center.pb-9.md\:pb-14 > div.ml-auto.flex.flex-row.items-center > svg').click()
                    değişken.click()
                    sleep(1)
                    try:
                        kod = driver.find_element(By.ID, "el-PLINE1").get_attribute("outerHTML")
                    except:
                        pass
                    try:
                        kod = driver.find_element(By.ID, "el-PLINE4").get_attribute("outerHTML")
                    except:
                        pass
                    tablolar = bs(kod, "lxml").find_all(class_="grid grid-cols-1 gap-y-8 md:grid-cols-2 md:gap-16")
                    for tablo in tablolar:
                        ürünler = tablo.find_all("section")
                        for ürün in ürünler:
                            ürün_linki = ana_link + ürün.a["href"]
                            try:
                                ürün_özellikleri = özellik_getir(ürün_linki)
                                ürün_özellikleri["product_id"] = f"{grup_id}-{len(grup_data['ürünler']) + 1}"
                                grup_data["ürünler"].append(ürün_özellikleri)
                                # print(ürün_özellikleri)
                            except Exception as err:
                                with open("hatalar.txt", "a", encoding="utf-8") as file:
                                    file.write(f"{err}, link {ürün_linki} grup_linki {grup_linki} \n")
            else:
                tablolar = grup_sitesi.find_all(class_="grid grid-cols-1 gap-y-8 md:grid-cols-2 md:gap-16")
                for tablo in tablolar:
                    ürünler = tablo.find_all("section")
                    for ürün in ürünler:
                        ürün_linki = ana_link + ürün.a["href"]
                        try:
                            ürün_özellikleri = özellik_getir(ürün_linki)
                            ürün_özellikleri["product_id"] = f"{grup_id}-{len(grup_data['ürünler']) + 1}"
                            grup_data["ürünler"].append(ürün_özellikleri)
                            # print(ürün_özellikleri)
                        except Exception as err:
                            with open("hatalar.txt", "a", encoding="utf-8") as file:
                                file.write(f"{err}, link {ürün_linki} grup_linki {grup_linki} \n")
        else:
            while True:
                try:
                    driver.get(grup_linki)
                    bekleme = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="el-submodels"]/section/div[1]/div[1]/a')))
                    link = driver.find_element(By.XPATH, '//*[@id="el-submodels"]/section/div[1]/div[1]/a').get_attribute("href")
                    driver.get(link + "&page=1000")
                    bekleme = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
                    bekleme = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product-container")))
                    break
                except:
                    pass

            anlık_sayfa = driver.find_element(By.XPATH, "/html").get_attribute("outerHTML")
            grup_ürünleri = bs(anlık_sayfa, "lxml").select(".product-container")
            for ürün in grup_ürünleri:
                ürün_linki = ana_link + ürün["href"]
                try:
                    ürün_özellikleri = özellik_getir(ürün_linki)
                    ürün_özellikleri["product_id"] = f"{grup_id}-{len(grup_data['ürünler']) + 1}"
                    grup_data["ürünler"].append(ürün_özellikleri)
                    # print(ürün_özellikleri)
                except Exception as err:
                    with open("hatalar.txt", "a", encoding="utf-8") as file:
                        file.write(f"{err}, link {ürün_linki} grup_linki {grup_linki} \n")
    elif "/subfamily" in aile_linki:
        deneme_sayacı = 0
        is_succeeded = False
        while deneme_sayacı < 5:
            try:
                driver.get(aile_linki)
                is_succeeded = True
                break
            except Exception as err:
                pass
        if not is_succeeded:
            with open("hatalar.txt", "a", encoding="utf-8") as file:
                file.write(f"aile sayfası açılmadı. {aile_linki}")
            continue

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "SCROLL_INVITATION_TARGET")))
        container = driver.find_element(By.ID, "SCROLL_INVITATION_TARGET").get_attribute("outerHTML")
        gruplar = bs(container, "lxml").find_all(class_="mt-16 mb-24 md:my-28")
        for grup in gruplar:
            grup_linki = ana_link + grup.a["href"]
            while True:
                try:
                    grup_sitesi = bs(requests.get(grup_linki).text, "lxml")
                    grup_adı = grup_sitesi.select_one(r".text-h4.leading-h4.md\:text-h3.md\:leading-h3").text.strip()
                    break
                except:
                    pass

            grup_id = f"{seri_id}-{harfler[len(seri_data['gruplar'])]}"
            grup_data = {
                "grup_data": {
                    "group_id": grup_id,
                    "group_name": grup_adı,
                    "group_link": grup_linki
                },
                "ürünler": []
            }
            seri_data["gruplar"][grup_adı] = grup_data

            grup_görselleri = [i["src"] for i in grup_sitesi.select(".main-swiper.swiper-container .swiper-slide img")]
            if len(grup_görselleri):
                grup_data["grup_data"]["group_image"] = grup_görselleri[0]
                grup_data["grup_data"]["application_images"] = grup_görselleri[1:]

            alt_gruplar_container = grup_sitesi.find_all(class_="items-card-container h-full")
            if len(alt_gruplar_container) == 0:
                if len(grup_sitesi.find_all(class_="inline-block mr-4")) != 0:
                    while True:
                        try:
                            driver.get(grup_linki)
                            değişkenler = driver.find_elements(By.CLASS_NAME, "inline-block mr-4")
                            break
                        except:
                            pass
                    if len(değişkenler) == 0:
                        try:
                            değişkenler = driver.find_elements(By.XPATH, '//*[@id="el-PLINE1"]/div[1]/div[2]/div[2]/div/div[1]/div/div/span')
                        except:
                            pass
                    for değişken in değişkenler:
                        driver.execute_script("arguments[0].click();", değişken)
                        sleep(1)
                        try:
                            kod = driver.find_element(By.ID, "el-PLINE1").get_attribute("outerHTML")
                        except:
                            pass
                        try:
                            kod = driver.find_element(By.ID, "el-PLINE4").get_attribute("outerHTML")
                        except:
                            pass
                        tablolar = bs(kod, "lxml").find_all(class_="grid grid-cols-1 gap-y-8 md:grid-cols-2 md:gap-16")
                        for tablo in tablolar:
                            ürünler = tablo.find_all("section")
                            for ürün in ürünler:
                                ürün_linki = ana_link + ürün.a["href"]
                                try:
                                    ürün_özellikleri = özellik_getir(ürün_linki)
                                    ürün_özellikleri["product_id"] = f"{grup_id}-{len(grup_data['ürünler']) + 1}"
                                    grup_data["ürünler"].append(ürün_özellikleri)
                                    # print(ürün_özellikleri)
                                except Exception as err:
                                    with open("hatalar.txt", "a", encoding="utf-8") as file:
                                        file.write(f"{err}, link {ürün_linki} grup_linki {grup_linki} \n")
                else:
                    tablolar = grup_sitesi.find_all(class_="grid grid-cols-1 gap-y-8 md:grid-cols-2 md:gap-16")
                    for tablo in tablolar:
                        ürünler = tablo.find_all("section")
                        for ürün in ürünler:
                            ürün_linki = ana_link + ürün.a["href"]
                            try:
                                ürün_özellikleri = özellik_getir(ürün_linki)
                                ürün_özellikleri["product_id"] = f"{grup_id}-{len(grup_data['ürünler']) + 1}"
                                grup_data["ürünler"].append(ürün_özellikleri)
                                # print(ürün_özellikleri)
                            except Exception as err:
                                with open("hatalar.txt", "a", encoding="utf-8") as file:
                                    file.write(f"{err}, link {ürün_linki} grup_linki {grup_linki} \n")
            else:
                while True:
                    try:
                        driver.get(grup_linki)
                        bekleme = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="el-submodels"]/section/div[1]/div[1]/a')))
                        link = driver.find_element(By.XPATH, '//*[@id="el-submodels"]/section/div[1]/div[1]/a').get_attribute("href")
                        driver.get(link + "&page=1000")
                        bekleme = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
                        bekleme = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product-container")))
                        break
                    except:
                        pass
                anlık_sayfa = driver.find_element(By.XPATH, "/html").get_attribute("outerHTML")
                grup_ürünleri = bs(anlık_sayfa, "lxml").find_all(class_="product-container")
                for ürün in grup_ürünleri:
                    ürün_linki = ana_link + ürün["href"]
                    try:
                        ürün_özellikleri = özellik_getir(ürün_linki)
                        ürün_özellikleri["product_id"] = f"{grup_id}-{len(grup_data['ürünler']) + 1}"
                        grup_data["ürünler"].append(ürün_özellikleri)
                        # print(ürün_özellikleri)
                    except Exception as err:
                        with open("hatalar.txt", "a", encoding="utf-8") as file:
                            file.write(f"{err}, link {ürün_linki} grup_linki {grup_linki} \n")

with open("database_son_flos_dec.json", "a", encoding="utf-8") as file:
    json.dump(urunler_json, file, ensure_ascii=False, indent=2)
