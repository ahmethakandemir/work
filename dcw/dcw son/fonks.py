from multiprocessing import cpu_count
import os
import json
import shutil
import requests
import urllib.request
from zipfile import ZipFile
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.request import urlopen
import tempfile
import contextlib
import ssl
import certifi

from urllib.error import ContentTooShortError
from urllib.parse import _splittype


def urlretrieve(url, filename=None, reporthook=None, data=None, context=None):
    _url_tempfiles = []
    url_type, path = _splittype(url)

    with contextlib.closing(urlopen(url, data, context=context)) as fp:
        headers = fp.info()

        # Just return the local path and the "headers" for file://
        # URLs. No sense in performing a copy unless requested.
        if url_type == "file" and not filename:
            return os.path.normpath(path), headers

        # Handle temporary file setup.
        if filename:
            tfp = open(filename, "wb")
        else:
            tfp = tempfile.NamedTemporaryFile(delete=False)
            filename = tfp.name
            _url_tempfiles.append(filename)

        with tfp:
            result = filename, headers
            bs = 1024 * 8
            size = -1
            read = 0
            blocknum = 0
            if "content-length" in headers:
                size = int(headers["Content-Length"])

            if reporthook:
                reporthook(blocknum, bs, size)

            while block := fp.read(bs):
                read += len(block)
                tfp.write(block)
                blocknum += 1
                if reporthook:
                    reporthook(blocknum, bs, size)

    if size >= 0 and read < size:
        raise ContentTooShortError(
            "retrieval incomplete: got only %i out of %i bytes" % (read, size), result
        )

    return result


# TODO test edilicek 19.10.23
def find_code(product_db, db):
    for family_name_db in db:
        for series_name_db in db[family_name_db]["seriler"]:
            for group_name_db in db[family_name_db]["seriler"][series_name_db][
                "gruplar"
            ]:
                for product in db[family_name_db]["seriler"][series_name_db]["gruplar"][
                    group_name_db
                ]["ürünler"]:
                    old_id = product_db.split("_")[0]
                    if old_id == product["product_id"]:
                        return product["ürün_kodu"]


# TODO düzenlenicek tekrar kullanılabilir olmalı 19.10.23
def to_dowloaded_json(downloads_link_based, db, dirs, download_name_based):
    for link in downloads_link_based:
        download_name = downloads_link_based[link]["download_name"]
        type = downloads_link_based[link]["type"]
        if not type:
            continue
        products = []
        products_db = downloads_link_based[link]["products"]
        for product_db in products_db:
            products.append(find_code(product_db))

        for b in downloads_link_based[link]["full_groups"]:
            for family_name_db in db:
                for series_name_db in db[family_name_db]["seriler"]:
                    for group_name_db in db[family_name_db]["seriler"][series_name_db][
                        "gruplar"
                    ]:
                        if (
                            not b.split("_")[0]
                            in db[family_name_db]["seriler"][series_name_db]["gruplar"][
                                group_name_db
                            ]["grup_data"]["group_id"]
                        ):
                            continue
                        for product in db[family_name_db]["seriler"][series_name_db][
                            "gruplar"
                        ][group_name_db]["ürünler"]:
                            products.append(product["ürün_kodu"])
        for a in downloads_link_based[link]["full_series"]:
            for family_name_db in db:
                for series_name_db in db[family_name_db]["seriler"]:
                    if (
                        not a.split("_")[0]
                        in db[family_name_db]["seriler"][series_name_db]["seri_data"][
                            "series_id"
                        ]
                    ):
                        continue
                    for group_name_db in db[family_name_db]["seriler"][series_name_db][
                        "gruplar"
                    ]:
                        for product in db[family_name_db]["seriler"][series_name_db][
                            "gruplar"
                        ][group_name_db]["ürünler"]:
                            products.append(product["ürün_kodu"])
        products = list(set(products))
        downloads_link_based[link]["products"] = products

        code = downloads_link_based[link]["code"]
        products = downloads_link_based[link]["products"]
        if not download_name in download_name_based:
            download_name_based[download_name] = {}
            download_name_based[download_name]["links"] = []
        download = {}
        download["link"] = link
        download["type"] = type
        download["code"] = code
        download["products"] = products

        if "surface" in type:
            download["folder"] = dirs["surface_images"] + "/"
        elif "polar" in type:
            download["folder"] = dirs["technical_images"] + "/"
        elif "application" in type:
            download["folder"] = dirs["application_images"] + "/"
        elif "technical" in type:
            download["folder"] = dirs["technical_images"] + "/"

        download["status"] = False
        download["name"] = download_name.replace(
            "ID", str(len(download_name_based[download_name]["links"]) + 1)
        )
        download_name_based[download_name]["links"].append(download)
    json_write("downloaded_1.json", download_name_based)


# 19.10.23
def to_excel_downloads(downloaded_json):
    to_excel_downloads = {}
    download_name_based = json_read(downloaded_json)
    for download_name in download_name_based:
        for download in download_name_based[download_name]["links"]:
            to_excel_downloads[download["link"]] = {}
            to_excel_downloads[download["link"]]["type"] = download["type"]
            to_excel_downloads[download["link"]]["products"] = download["products"]
            to_excel_downloads[download["link"]]["download_name"] = download["name"]
            to_excel_downloads[download["link"]]["status"] = download["status"]

    json_write("to_excel_downloads.json", to_excel_downloads)


# 13.06.23
def empty():
    return


import requests


def get_file_metadata(url):
    try:
        response = requests.head(url)
        if response.status_code == 200:
            # Metadata can be extracted from the response headers
            content_type = response.headers.get("Content-Type")
            content_length = response.headers.get("Content-Length")
            last_modified = response.headers.get("Last-Modified")

            return {
                "Content-Type": content_type,
                "Content-Length": content_length,
                "Last-Modified": last_modified,
            }
        else:
            print(f"Error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")

    return None


# 9.6.23
def get_soup(link):
    link = requests.get(link)
    link = bs(link.text, "html.parser")
    return link


def get_instant_html_2(link, cookie=True):
    if cookie:
        coo_path = r"C:\iCloudDrive\iCloud Kitoko\ortak\cookies.crx"
        options = webdriver.ChromeOptions()
        options.add_extension(coo_path)
        driver = webdriver.Chrome(options=options)
    else:
        driver = webdriver.Chrome()
    try:
        driver.switch_to.window(driver.window_handles[0])
        driver.execute_script(f"window.open();")
        driver.switch_to.window(driver.window_handles[1])

        driver.get(link)
        # driver.maximize_window()
        anlık_sayfa = driver.find_element(By.XPATH, "/html")
        html = anlık_sayfa.get_attribute("outerHTML")
        soup_2 = bs(html, "html.parser")
        driver.close()
    except:
        print("internet hatası")
        soup_2 = get_instant_html_2(link, driver)
    return soup_2


# 10.6.23
def get_instant_html(link, driver="!ok"):
    if driver == "!ok":
        driver = webdriver.Chrome()

    driver.switch_to.window(driver.window_handles[0])
    driver.execute_script(f"window.open();")
    driver.switch_to.window(driver.window_handles[1])

    driver.get(link)
    # driver.maximize_window()
    # pre_action(link, driver)
    instant_page = driver.find_element(By.XPATH, "/html")
    link = bs(instant_page.text, "html.parser")
    soup_2 = bs(link, "html.parser")
    return soup_2


# 9.6.23
def zip_folder(zip_name, folder_name):
    shutil.make_archive(zip_name, "zip", folder_name)


# 9.6.23
def extract_all_files(folder, toFolder):
    for a in os.scandir(folder):
        if os.path.isdir(a):
            extract_all_files(a.path, toFolder)
        else:
            os.replace(a, toFolder + a.name)


# 9.6.23
def clean_except_this(path, this, really=False):
    if not really:
        for a in os.scandir(path):
            if os.path.isdir(a.path):
                clean_except_this(a.path, this)
            elif not os.path.splitext(a.name)[1].lower() in this:
                try:
                    os.remove(a)
                except:
                    shutil.rmtree(a)
    else:
        for a in os.scandir(path):
            if not os.path.splitext(a.name)[1].lower() in this:
                try:
                    os.remove(a)
                except:
                    shutil.rmtree(a)


# 9.6.23
def clean_just_this(path, this, really=False):
    if not really:
        for a in os.scandir(path):
            if os.path.isdir(a.path):
                clean_just_this(a.path, this)
            elif os.path.splitext(a.name)[1].lower() in this:
                if not os.path.splitext(a.name)[1].lower() == ".py":
                    try:
                        os.remove(a)
                    except:
                        shutil.rmtree(a)
    else:
        for a in os.scandir(path):
            if not os.path.splitext(a.name)[1].lower() in this:
                try:
                    os.remove(a)
                except:
                    shutil.rmtree(a)


# 9.6.23
def makeList_byExtensions(path, extension_1):
    one_list = []
    for a in os.scandir(path):
        abc = os.path.splitext(a.name)
        if os.path.splitext(a.name)[1].lower() == extension_1:
            one_list.append(a.path)
        if os.path.isdir(a.path):
            one_list += makeList_byExtensions(a.path, extension_1)
    return one_list


# 9.6.23
def unzip(zipFile_dir):
    for a in os.listdir(zipFile_dir):
        if a.endswith(".zip"):
            with ZipFile(a, "r") as zipObj:
                zipObj.extractall(zipFile_dir + "mainZip/")


# 9.6.23
def make_zip(files_list: list, zip_name, where):
    zipObj = ZipFile(zip_name, "w")

    for file in files_list:
        if not file.endswith(".py"):
            ali = file.split("\\")[-1]
            shutil.copy2(file, "./" + file.split("/")[-1])
            zipObj.write(file, "./" + file.split("/")[-1])
            os.remove("./" + file.split("/")[-1])
    zipObj.close()
    os.replace(zip_name, where + zip_name)


# 9.6.23
def json_read(jsonName):
    f = open(jsonName, encoding="utf8")
    ret = json.load(f)
    f.close()
    return ret


# 9.6.23
def json_write(jsonName, data):
    class SetEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, set):
                return list(obj)
            return json.JSONEncoder.default(self, obj)

    with open(jsonName, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=SetEncoder)


# 13.9.23
def download(what, where, download_Name, try_number=3, del_after=False, pre_link=False):
    if del_after:
        what = what.split("?")[0]
    if not not pre_link:
        what = pre_link + what
    for i in range(try_number):
        if os.path.isfile(f"{where}{download_Name}"):
            print("inmiş : " + download_Name)
            return True

        try:
            urllib.request.urlretrieve(what, where + download_Name)
            print("inmiş : " + download_Name)

            return True
        except:
            where = where.replace(
                "C:/Users/User/Desktop/download", "C:/iCloudDrive/iCloud Kitoko/delta"
            )
            what = what.replace(" ", "%20")
            opener = urllib.request.build_opener()

            opener.addheaders = [
                (
                    "User-Agent",
                    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36",
                )
            ]

            try:
                context = ssl._create_unverified_context()
                ssl._create_default_https_context = ssl._create_unverified_context
                urllib.request.urlretrieve(what, where + download_Name)

                print("inmiş : " + download_Name)
                return True
            except:
                print("İNMEDİ : " + download_Name)
                return False


# 10.06.23 eksik
def delay(driver, delay):
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By

    myElem = WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((By.ID, "IdOfMyElement"))
    )


harfler = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "AA",
    "AB",
    "AC",
    "AD",
    "AE",
    "AF",
    "AG",
    "AH",
    "AI",
    "AJ",
    "AK",
    "AL",
    "AM",
    "AN",
    "AO",
    "AP",
    "AQ",
    "AR",
    "AS",
    "AT",
    "AU",
    "AV",
    "AW",
    "AX",
    "AY",
    "AZ",
    "BA",
    "BB",
    "BC",
    "BD",
    "BE",
    "BF",
    "BG",
    "BH",
    "BI",
    "BJ",
    "BK",
    "BL",
    "BM",
    "BN",
    "BO",
    "BP",
    "BQ",
    "BR",
    "BS",
    "BT",
    "BU",
    "BV",
    "BW",
    "BX",
    "BY",
    "BZ",
    "CA",
    "CB",
    "CC",
    "CD",
    "CE",
    "CF",
    "CG",
    "CH",
    "CI",
    "CJ",
    "CK",
    "CL",
    "CM",
    "CN",
    "CO",
    "CP",
    "CQ",
    "CR",
    "CS",
    "CT",
    "CU",
    "CV",
    "CW",
    "CX",
    "CY",
    "CZ",
    "DA",
    "DB",
    "DC",
    "DD",
    "DE",
    "DF",
    "DG",
    "DH",
    "DI",
    "DJ",
    "DK",
    "DL",
    "DM",
    "DN",
    "DO",
    "DP",
    "DQ",
    "DR",
    "DS",
    "DT",
    "DU",
    "DV",
    "DW",
    "DX",
    "DY",
    "DZ",
    "EA",
    "EB",
    "EC",
    "ED",
    "EE",
    "EF",
    "EG",
    "EH",
    "EI",
    "EJ",
    "EK",
    "EL",
    "EM",
    "EN",
    "EO",
    "EP",
    "EQ",
    "ER",
    "ES",
    "ET",
    "EU",
    "EV",
    "EW",
    "EX",
    "EY",
    "EZ",
    "FA",
    "FB",
    "FC",
    "FD",
    "FE",
    "FF",
    "FG",
    "FH",
    "FI",
    "FJ",
    "FK",
    "FL",
    "FM",
    "FN",
    "FO",
    "FP",
    "FQ",
    "FR",
    "FS",
    "FT",
    "FU",
    "FV",
    "FW",
    "FX",
    "FY",
    "FZ",
    "GA",
    "GB",
    "GC",
    "GD",
    "GE",
    "GF",
    "GG",
    "GH",
    "GI",
    "GJ",
    "GK",
    "GL",
    "GM",
    "GN",
    "GO",
    "GP",
    "GQ",
    "GR",
    "GS",
    "GT",
    "GU",
    "GV",
    "GW",
    "GX",
    "GY",
    "GZ",
    "HA",
    "HB",
    "HC",
    "HD",
    "HE",
    "HF",
    "HG",
    "HH",
    "HI",
    "HJ",
    "HK",
    "HL",
    "HM",
    "HN",
    "HO",
    "HP",
    "HQ",
    "HR",
    "HS",
    "HT",
    "HU",
    "HV",
    "HW",
    "HX",
    "HY",
    "HZ",
    "IA",
    "IB",
    "IC",
    "ID",
    "IE",
    "IF",
    "IG",
    "IH",
    "II",
    "IJ",
    "IK",
    "IL",
    "IM",
    "IN",
    "IO",
    "IP",
    "IQ",
    "IR",
    "IS",
    "IT",
    "IU",
    "IV",
    "IW",
    "IX",
    "IY",
    "IZ",
    "JA",
    "JB",
    "JC",
    "JD",
    "JE",
    "JF",
    "JG",
    "JH",
    "JI",
    "JJ",
    "JK",
    "JL",
    "JM",
    "JN",
    "JO",
    "JP",
    "JQ",
    "JR",
    "JS",
    "JT",
    "JU",
    "JV",
    "JW",
    "JX",
    "JY",
    "JZ",
    "KA",
    "KB",
    "KC",
    "KD",
    "KE",
    "KF",
    "KG",
    "KH",
    "KI",
    "KJ",
    "KK",
    "KL",
    "KM",
    "KN",
    "KO",
    "KP",
    "KQ",
    "KR",
    "KS",
    "KT",
    "KU",
    "KV",
    "KW",
    "KX",
    "KY",
    "KZ",
    "LA",
    "LB",
    "LC",
    "LD",
    "LE",
    "LF",
    "LG",
    "LH",
    "LI",
    "LJ",
    "LK",
    "LL",
    "LM",
    "LN",
    "LO",
    "LP",
    "LQ",
    "LR",
    "LS",
    "LT",
    "LU",
    "LV",
    "LW",
    "LX",
    "LY",
    "LZ",
    "MA",
    "MB",
    "MC",
    "MD",
    "ME",
    "MF",
    "MG",
    "MH",
    "MI",
    "MJ",
    "MK",
    "ML",
    "MM",
    "MN",
    "MO",
    "MP",
    "MQ",
    "MR",
    "MS",
    "MT",
    "MU",
    "MV",
    "MW",
    "MX",
    "MY",
    "MZ",
    "NA",
    "NB",
    "NC",
    "ND",
    "NE",
    "NF",
    "NG",
    "NH",
    "NI",
    "NJ",
    "NK",
    "NL",
    "NM",
    "NN",
    "NO",
    "NP",
    "NQ",
    "NR",
    "NS",
    "NT",
    "NU",
    "NV",
    "NW",
    "NX",
    "NY",
    "NZ",
    "OA",
    "OB",
    "OC",
    "OD",
    "OE",
    "OF",
    "OG",
    "OH",
    "OI",
    "OJ",
    "OK",
    "OL",
    "OM",
    "ON",
    "OO",
    "OP",
    "OQ",
    "OR",
    "OS",
    "OT",
    "OU",
    "OV",
    "OW",
    "OX",
    "OY",
    "OZ",
    "PA",
    "PB",
    "PC",
    "PD",
    "PE",
    "PF",
    "PG",
    "PH",
    "PI",
    "PJ",
    "PK",
    "PL",
    "PM",
    "PN",
    "PO",
    "PP",
    "PQ",
    "PR",
    "PS",
    "PT",
    "PU",
    "PV",
    "PW",
    "PX",
    "PY",
    "PZ",
    "QA",
    "QB",
    "QC",
    "QD",
    "QE",
    "QF",
    "QG",
    "QH",
    "QI",
    "QJ",
    "QK",
    "QL",
    "QM",
    "QN",
    "QO",
    "QP",
    "QQ",
    "QR",
    "QS",
    "QT",
    "QU",
    "QV",
    "QW",
    "QX",
    "QY",
    "QZ",
    "RA",
    "RB",
    "RC",
    "RD",
    "RE",
    "RF",
    "RG",
    "RH",
    "RI",
    "RJ",
    "RK",
    "RL",
    "RM",
    "RN",
    "RO",
    "RP",
    "RQ",
    "RR",
    "RS",
    "RT",
    "RU",
    "RV",
    "RW",
    "RX",
    "RY",
    "RZ",
    "SA",
    "SB",
    "SC",
    "SD",
    "SE",
    "SF",
    "SG",
    "SH",
    "SI",
    "SJ",
    "SK",
    "SL",
    "SM",
    "SN",
    "SO",
    "SP",
    "SQ",
    "SR",
    "SS",
    "ST",
    "SU",
    "SV",
    "SW",
    "SX",
    "SY",
    "SZ",
    "TA",
    "TB",
    "TC",
    "TD",
    "TE",
    "TF",
    "TG",
    "TH",
    "TI",
    "TJ",
    "TK",
    "TL",
    "TM",
    "TN",
    "TO",
    "TP",
    "TQ",
    "TR",
    "TS",
    "TT",
    "TU",
    "TV",
    "TW",
    "TX",
    "TY",
    "TZ",
    "UA",
    "UB",
    "UC",
    "UD",
    "UE",
    "UF",
    "UG",
    "UH",
    "UI",
    "UJ",
    "UK",
    "UL",
    "UM",
    "UN",
    "UO",
    "UP",
    "UQ",
    "UR",
    "US",
    "UT",
    "UU",
    "UV",
    "UW",
    "UX",
    "UY",
    "UZ",
    "VA",
    "VB",
    "VC",
    "VD",
    "VE",
    "VF",
    "VG",
    "VH",
    "VI",
    "VJ",
    "VK",
    "VL",
    "VM",
    "VN",
    "VO",
    "VP",
    "VQ",
    "VR",
    "VS",
    "VT",
    "VU",
    "VV",
    "VW",
    "VX",
    "VY",
    "VZ",
    "WA",
    "WB",
    "WC",
    "WD",
    "WE",
    "WF",
    "WG",
    "WH",
    "WI",
    "WJ",
    "WK",
    "WL",
    "WM",
    "WN",
    "WO",
    "WP",
    "WQ",
    "WR",
    "WS",
    "WT",
    "WU",
    "WV",
    "WW",
    "WX",
    "WY",
    "WZ",
    "XA",
    "XB",
    "XC",
    "XD",
    "XE",
    "XF",
    "XG",
    "XH",
    "XI",
    "XJ",
    "XK",
    "XL",
    "XM",
    "XN",
    "XO",
    "XP",
    "XQ",
    "XR",
    "XS",
    "XT",
    "XU",
    "XV",
    "XW",
    "XX",
    "XY",
    "XZ",
    "YA",
    "YB",
    "YC",
    "YD",
    "YE",
    "YF",
    "YG",
    "YH",
    "YI",
    "YJ",
    "YK",
    "YL",
    "YM",
    "YN",
    "YO",
    "YP",
    "YQ",
    "YR",
    "YS",
    "YT",
    "YU",
    "YV",
    "YW",
    "YX",
    "YY",
    "YZ",
    "ZA",
    "ZB",
    "ZC",
    "ZD",
    "ZE",
    "ZF",
    "ZG",
    "ZH",
    "ZI",
    "ZJ",
    "ZK",
    "ZL",
    "ZM",
    "ZN",
    "ZO",
    "ZP",
    "ZQ",
    "ZR",
    "ZS",
    "ZT",
    "ZU",
    "ZV",
    "ZW",
    "ZX",
    "ZY",
    "ZZ",
    "hamarat",
]


def download_name(pre_name, download_number, mode):
    # ----images---
    if mode == "surface":
        uzanti = "jpg"
        download_name = f"{pre_name}S-{download_number}.{uzanti}"

    elif "reference" in mode:
        uzanti = "jpg"
        download_name = f"{pre_name}Reference-{download_number}.{uzanti}"

    elif mode == "technical" or mode == "polar_diagram":
        # uzanti = "svg"
        uzanti = "jpg"
        download_name = f"{pre_name}Technical.{uzanti}"

    return download_name


def dests(main_dir):
    return {
        "surface": f"{main_dir}/surfaces/",
        "reference": f"{main_dir}/references/",
        "pdf": f"{main_dir}/pdfs/",
        "others_dir": f"{main_dir}/others/",
        "technical": f"{main_dir}/others/",
        "polar_diagram": f"{main_dir}/others/",
        "datasheet_text": f"{main_dir}/others/",
    }
