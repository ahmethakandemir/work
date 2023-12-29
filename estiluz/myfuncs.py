import json

jsondata = {}

def tofile(jsondata,initial_id = 0):
    addId(jsondata,initial_id)
    with open("data.json", 'w', encoding="utf-8") as outfile:
        json.dump(jsondata, outfile, indent=2, ensure_ascii=False)
    
#and write harfler array from a to zz
harfler = []    # harfler is A to Z and continued like AA,AB,AC to ,ZZ
for i in range(65,91):
    harfler.append(chr(i))
for i in range(65,91):
    for j in range(65,91):
        harfler.append(chr(i)+chr(j))

initial_id = 0
def addId(jsondata,initial_id):
    # id will added to jsondata as family_id = initial_id + ailecounter, series_id = family_id-"harfcounter" : like 700006-A, group_id = series_id-"sayicounter" : like 700006-A-1
    ailecounter = 0
    for aile in jsondata:
        jsondata[aile]["aile_data"]["family_id"] = str(initial_id + ailecounter)
        seri_counter = 0
        for seri in jsondata[aile]["seriler"]:
            seri_counter += 1
            jsondata[aile]["seriler"][seri]["seri_data"]["series_id"] = str(initial_id + ailecounter) + "-" + harfler[seri_counter-1]
            grup_counter = 0
            for grup in jsondata[aile]["seriler"][seri]["gruplar"]:
                grup_counter += 1
                jsondata[aile]["seriler"][seri]["gruplar"][grup]["grup_data"]["group_id"] = str(initial_id + ailecounter) + "-" + harfler[seri_counter-1] + "-" + str(grup_counter)
                #create product_id for each product
                urunlerlist = jsondata[aile]["seriler"][seri]["gruplar"][grup]["urunler"]
                uruncounter = 0
                for urun in urunlerlist:
                    uruncounter += 1
                    urun["product_id"] = str(initial_id + ailecounter) + "-" + harfler[seri_counter-1] + "-" + str(grup_counter) + "-" + harfler[uruncounter-1]
                    
        ailecounter += 40   
    return jsondata
