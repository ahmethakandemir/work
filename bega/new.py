import json

jsonlist = {}

aileler = ["aile1", "aile2"]

# Initialize "aileler" as an empty dictionary

# Create an empty dictionary for each "aile"
for aile in aileler:
    jsonlist[aile] = aile_dict = {}     # Create an empty dictionary for each "aile"
    jsonlist[aile]["ailedata"] = ailedata = {} # Create an empty dictionary for each "ailedata"
    aile_dict["seriler"] = {}
    seriler = ["seri1", "seri2"]

    # Create an empty dictionary for each "seri"
    for seri in seriler:
        
        aile_dict["seriler"][seri] = seri_dict = {}
        seri_dict["seridata"] = seridata = {}
        
        
        gruplar = ["grup1", "grup2"]

        # Create an empty dictionary for each "grup"
        for grup in gruplar:
            # Update the nested structure with your desired values
            seri_dict[grup] = f"value_for_{grup}"

# Save the updated jsonlist to a file
with open('new.json', 'w') as outfile:
    json.dump(jsonlist, outfile, indent=2)

# Print the updated JSON structure
print(json.dumps(jsonlist, indent=2))

