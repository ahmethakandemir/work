import fonks as _


brand = "dcw"

db_dir = rf".\idli_db_{brand}.json"
db_dir = rf".\{brand}_data.json"
db = _.json_read(db_dir)

for family_name in db:
    for series_name in db[family_name]["seriler"]:
        for group_name in db[family_name]["seriler"][series_name]["gruplar"]:
            for product in db[family_name]["seriler"][series_name]["gruplar"][
                group_name
            ]["ürünler"].copy():
                if "customizations" in product:
                    customizations = product["customizations"].copy()
                    del product["customizations"]
                else:
                    continue
                old_product = product.copy()

                if isinstance(customizations, list):
                    print("ok")

                    for custom_dict in customizations:
                        new_product = old_product.copy()
                        product_image = custom_dict["img"]
                        for custom_color in custom_dict:
                            if custom_color == "img":
                                continue
                            new_product["product_name"] += (
                                "_" + custom_color.capitalize()
                            )
                        db[family_name]["seriler"][series_name]["gruplar"][group_name][
                            "ürünler"
                        ].append(new_product)
                else:
                    for custom_color in customizations:
                        new_product = old_product.copy()
                        new_product["product_name"] += "_" + custom_color.capitalize()

                        product_image = customizations[custom_color]
                        new_product["product_image"] = product_image

                        db[family_name]["seriler"][series_name]["gruplar"][group_name][
                            "ürünler"
                        ].append(new_product)


_.json_write("deneme_data_rev.json", db)


print(uni_keys)
