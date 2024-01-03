import json

with open('estiluzdata.json', 'r', encoding="utf-8") as json_file:
    data = json.load(json_file)

log = open('log.txt','w',encoding="utf-8")   

for aile in data:
    for seri in data[aile]["seriler"]:
        for grup in data[aile]["seriler"][seri]["gruplar"]:
            for urun in data[aile]["seriler"][seri]["gruplar"][grup]["urunler"]:


                if urun['application_images'] == [] and urun['product_images'] == []:
                    log.write(urun["product_name"] + " empty product and application images\n")
                
log.close()

a = open("log.txt" , "r", encoding="utf-8")
b = a.read()

while "\n\n" in b:
    b = b.replace("\n\n","\n")
with open("log.txt" , "w", encoding="utf-8") as f:
    f.write(b)
a.close()