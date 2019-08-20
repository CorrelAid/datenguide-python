import pandas as pd

from pandas.io.json import json_normalize

from typing import Dict, Any


class QueryOutputTransformer:
    """ IN PROGRESS only region query to do: DOKU """

    def __init__(self):
        pass

    @staticmethod
    def build_and_merge_data_region_query(
        query_response_json: Dict[str, Any]
    ) -> pd.DataFrame:
        whole_data_body = json_normalize(query_response_json)
        # potentially incomplete list [id, name] ... what else?
        temp_list = ["data.region.id", "data.region.name"]
        col_list_whole_data_body = [
            col for col in whole_data_body.columns if col not in temp_list
        ]

        flat_json_dict = {}

        i = 0

        for c in col_list_whole_data_body:
            flat_json_dict[f"{c}"] = json_normalize(query_response_json)[
                col_list_whole_data_body[i]
            ]
            i = i + 1

        for i in range(len(col_list_whole_data_body)):
            locals()[f"data_0{i}"] = json_normalize(
                flat_json_dict[col_list_whole_data_body[i]][0]
            )
            # w/ type (e.g. GES)
            try:
                locals()[f"data{i}"] = (
                    locals()[f"data_0{i}"]
                    .pivot(index="year", columns="type", values="value")
                    .reset_index()
                )
                cols = list(locals()[f"data{i}"].columns)
                new_cols = [
                    x.replace(
                        "GES",
                        col_list_whole_data_body[i].replace("data.region.", "")
                        + "_GES",
                    )
                    for x in cols
                ]
                locals()[f"data{i}"].columns = new_cols
                # w/o type
            except KeyError:
                locals()[f"data{i}"] = locals()[f"data_0{i}"]
                cols = list(locals()[f"data{i}"].columns)
                cols_temp = [
                    col_list_whole_data_body[i].replace("data.region.", "") + "_" + x
                    for x in cols
                ]
                cols_temp3 = [
                    x.replace(
                        col_list_whole_data_body[i].replace("data.region.", "")
                        + "_year",
                        "year",
                    )
                    for x in cols_temp
                ]
                new_cols = [x.replace("data.region.", "") for x in cols_temp3]
                locals()["data{}".format(i)].columns = new_cols
            try:
                locals()["data{}".format(i)]["id"] = whole_data_body["data.region.id"][
                    0
                ]
            except KeyError:
                print(col_list_whole_data_body[i] + " has no id")
                pass
            try:
                locals()["data{}".format(i)]["name"] = whole_data_body[
                    "data.region.name"
                ][0]
            except KeyError:
                print(col_list_whole_data_body[i] + " has no name")
                pass

        data_out = locals()[f"data_0{0}"]
        for l in range(1, len(col_list_whole_data_body)):
            data_out["fake_id"] = 1
            locals()[f"data{l}"]["fake_id"] = 1
            data_out = data_out.merge(locals()[f"data{l}"], how="outer")
            cols = list(data_out.columns)
            cols.remove("fake_id")
            data_out = data_out[cols]

        return data_out

    @classmethod
    def transform(cls, query_response):
        output = cls.build_and_merge_data_region_query(query_response)
        return output
