import json
from myfuncs import addId
data = {}
with open('data.json', 'r', encoding="utf-8") as json_file:
    data = json.load(json_file)
    
images = {}
with open('estiluzimages.json', 'r', encoding="utf-8") as json_file:
    images = json.load(json_file)

product_names = {}

for aile in data:
    for seri in data[aile]["seriler"]:
        for grup in data[aile]["seriler"][seri]["gruplar"]:
            for urun in data[aile]["seriler"][seri]["gruplar"][grup]["urunler"]:
                proname = urun["product_name"]
                fullad = proname.split(' ')
                urunjson = {}
                if '+' in urun["product_name"]:
                    index = fullad.index('+')
                    urunadi = fullad[index-1]

                elif '/' not in urun["product_name"]:
                    urunadi = fullad[-1]
                else:
                    fullad = proname.split('/')
                    for i in range(len(fullad)):
                        fullad[i] = fullad[i].strip()
                    
                    leng = len(fullad)
                    last_word = fullad[0].split(' ')[-1]
                    result = last_word + '/' + '/'.join(fullad[1:])
                    urunadi = result
                urunjson["aile"] = aile
                urunjson["seri"] = seri
                urunjson["grup"] = grup
                urunjson["urun"] = proname
                urunjson["product_images"] = []
                urunjson["application_images"] = []
                product_names[urunadi] = urunjson

    
for img in images:
    splitted = images[img]["foto_adi"].split('_')
    urunkodlari = []
    for i in range(len(splitted)):
        splitted[i] = splitted[i].strip()
        if '.' or '-' in splitted[i]:
            urunkodlari.append(splitted[i])
    for product in product_names:
        if product in urunkodlari:
            if 'p' in images[img]["foto_adi"].split('_')[-1]:
                product_names[product]["product_images"].append(images[img])
            elif 'a' in images[img]["foto_adi"].split('_')[-1]:
                product_names[product]["application_images"].append(images[img])
    


with open('estiluzproductnames.json', 'w', encoding="utf-8") as json_file:
    json.dump(product_names, json_file, ensure_ascii=False, indent=4)

for product in product_names:
    for urun in data[product_names[product]["aile"]]["seriler"][product_names[product]["seri"]]["gruplar"][product_names[product]["grup"]]["urunler"]:
        if urun["product_name"] == product_names[product]["urun"]:
            urun["product_images"] = product_names[product]["product_images"]
            urun["application_images"] = product_names[product]["application_images"]
            

        
        
addId(data,700009)
    
with open('estiluzdata.json', 'w', encoding="utf-8") as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)
