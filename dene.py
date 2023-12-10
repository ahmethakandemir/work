import json

jsondata = {}

with open('data.json', 'r') as infile:
    jsondata = json.load(infile)
    
with open('data.json', 'w', encoding="utf-8") as outfile:
    json.dump(jsondata, outfile, indent=2)