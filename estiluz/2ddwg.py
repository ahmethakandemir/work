import json

productnames = {}

with open('estiluzproductnames.json', 'r', encoding="utf-8") as json_file:
    productnames = json.load(json_file)

for product in productnames["products"]:
    #remove product_images and application_images completely
    product.pop("product_images",None)
    product.pop("application_images",None)
    

with open('estiluzproducts.json', 'w', encoding="utf-8") as json_file:
    json.dump(productnames, json_file, indent=2, ensure_ascii=False)
    
