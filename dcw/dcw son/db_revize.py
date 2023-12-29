from myP import fonks as _


# Değişkenler
brand = "dcw"
_id = 700006
change_ids = True
#

_id -= 40
db_dir = rf".\idli_db_{brand}.json"


db = _.json_read(db_dir)
letters = _.harfler


# indirme json'ı idli_json'a ekler
def add_downloads_to_db(_id):
    down_db_dir = rf".\{brand}_raw_download.json"
    down_db = _.json_read(down_db_dir)
    for a in down_db:
        p_name = a["product_name"]
        if p_name == _id:
            product[a["type"]] = {}
            product[a["type"]]["link"] = a["link"]
            product[a["type"]]["extension"] = a["extension"]


# aileden ürüne id ekler ve dosya pre_name ekler
control_list = []
for family_name in db:
    _id += 40
    series_id = 0

    if change_ids:
        db[family_name]["aile_data"]["family_id"] = str(_id)

    for series_name in db[family_name]["seriler"]:
        series_id += 1
        group_index = 0
        if change_ids:
            db[family_name]["seriler"][series_name]["seri_data"]["series_id"] = (
                str(_id) + "-" + str(series_id)
            )
        for group_name in db[family_name]["seriler"][series_name]["gruplar"]:
            group_index += 1
            product_id = 0

            if change_ids:
                db[family_name]["seriler"][series_name]["gruplar"][group_name][
                    "grup_data"
                ]["group_id"] = (
                    str(_id) + "-" + str(series_id) + "-" + letters[group_index - 1]
                )
            for product in db[family_name]["seriler"][series_name]["gruplar"][
                group_name
            ]["ürünler"]:
                product_id += 1
                product["product_id"] = (
                    str(_id)
                    + "-"
                    + str(series_id)
                    + "-"
                    + letters[group_index - 1]
                    + "-"
                    + str(product_id)
                )
                print(product["product_id"])
                # _x = product["product_slider_images"]
                # product["product_slider_images"] = _x[2:]
                # product["product_slider_images_technical"] = _x[0:2]
                # add_downloads_to_db(product["product_name"])

_.json_write(f"idli_db_{brand}.json", db)
