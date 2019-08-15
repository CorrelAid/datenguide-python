import pandas as pd

from pandas.io.json import json_normalize

from typing import Dict, Any

from pandas.errors import MergeError


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
            flat_json_dict["{}".format(c)] = json_normalize(query_response_json)[
                col_list_whole_data_body[i]
            ]
            i = i + 1

        for i in range(len(col_list_whole_data_body)):
            globals()["datatemp{}".format(i)] = json_normalize(
                flat_json_dict[col_list_whole_data_body[i]][0]
            )
            # w/ type (e.g. GES)
            try:
                globals()["data{}".format(i)] = (
                    globals()["datatemp{}".format(i)]
                    .pivot(index="year", columns="type", values="value")
                    .reset_index()
                )
                cols = list(globals()["data{}".format(i)].columns)
                new_cols = [
                    x.replace(
                        "GES",
                        col_list_whole_data_body[i].replace("data.region.", "")
                        + "_GES",
                    )
                    for x in cols
                ]
                globals()["data{}".format(i)].columns = new_cols
            # w/o type
            except KeyError:
                globals()["data{}".format(i)] = globals()["datatemp{}".format(i)]
                cols = list(globals()["data{}".format(i)].columns)
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
                globals()["data{}".format(i)].columns = new_cols
            try:
                globals()["data{}".format(i)]["id"] = whole_data_body["data.region.id"][
                    0
                ]
            except KeyError:
                print(col_list_whole_data_body[i] + " has no id")
                pass
            try:
                globals()["data{}".format(i)]["name"] = whole_data_body[
                    "data.region.name"
                ][0]
            except KeyError:
                print(col_list_whole_data_body[i] + " has no name")
                pass

        data_out = globals()["data{}".format(0)]
        for l in range(1, len(col_list_whole_data_body)):
            try:
                data_out = data_out.merge(globals()["data{}".format(l)], how="outer")
            except MergeError:
                print("no joint key to merge on")
                data_out["fake_id"] = 1
                globals()["data{}".format(l)]["fake_id"] = 1
                data_out = data_out.merge(globals()["data{}".format(l)], how="outer")
                cols = list(data_out.columns)
                cols.remove("fake_id")
                data_out = data_out[cols]

        return data_out

    @classmethod
    def transform(cls, query_response):
        output = cls.build_and_merge_data_region_query(query_response)
        return output
