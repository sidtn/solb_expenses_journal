import json


def write_category_json(file_name):
    categories_list = []
    pk_index = 1
    with open (file_name, "r", encoding="utf-8") as file:
        for line in file:
            category_dict = {
                "fields": {
                    "name": line.strip(),
                    "owner": None
                },
                "model": "journal_api.category",
                "pk": pk_index,
            }
            pk_index += 1
            categories_list.append(category_dict)

    with open("categories.json", "w", encoding="utf8") as json_file:
        json_data = json.dumps(categories_list, ensure_ascii=False, sort_keys=True, indent=4)
        json_file.write(json_data)


if __name__ == "__main__":
    write_category_json("categories.txt")
