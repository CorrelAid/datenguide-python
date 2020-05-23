import os
import json


def get_schema_json():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(curr_dir, "package_data")
    schema_json_path = os.path.join(data_dir, "schema.json")
    with open(schema_json_path, "r") as schema_file:
        full_json = json.load(schema_file)

    return full_json


def get_simple_json_path(json, path_list):
    if json is None or len(path_list) == 0:
        return json
    else:
        return get_simple_json_path(json.get(path_list[0]), path_list[1:])


def get_json_path(json, path_list, default="Missing"):
    if json == [] or len(path_list) == 0:
        return json
    else:
        next_val = path_list[0]
        if next_val == "..":
            return [
                elem
                for sub_j in json
                for v in sub_j.values()
                for elem in get_json_path([v], path_list[1:])
            ]
        elif len(path_list) == 1:
            return [sub_j.get(next_val, default) for sub_j in json]
        else:
            sub_jsons = [sub_j for sub_j in json if sub_j.get(next_val) is not None]
            return [
                elem
                for sub_j in sub_jsons
                for elem in get_json_path([sub_j.get(next_val)], path_list[1:])
            ]


if __name__ == "__main__":
    full_json = get_schema_json()
    print(list(get_simple_json_path(full_json, ["22221", "measures", "RLE001"]).keys()))
    stat_names = get_json_path([full_json], ["..", "measures", "..", "name"])
    stat_descr = get_json_path([full_json], ["..", "measures", "..", "definition_de"])

    print(
        list(
            get_json_path([full_json], ["..", "measures", "..", "dimensions", "NAT"])[
                0
            ].keys()
        )
    )
    print(
        get_json_path(
            [full_json], ["..", "measures", "..", "dimensions", "NAAT", "value_names"]
        )
    )
