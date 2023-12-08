import json

with open('data.json', 'r') as infile:
    jsondata = json.load(infile)
    
with open('data.json', 'w') as outfile:
    json.dump(jsondata, outfile, indent=2)