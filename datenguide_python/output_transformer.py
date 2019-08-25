import pandas as pd

from pandas.io.json import json_normalize

from typing import Dict, Any


class QueryOutputTransformer:
    """ IN PROGRESS only region query to do: DOKU """

    def __init__(self, query_response_json: Dict[str, Any]):
        self.whole_data_body = json_normalize(query_response_json)
        self.query_data: Dict[str, Any] = {}
        self.default_list = ["data.region.id", "data.region.name"]
        self.flat_json_dict: Dict[str, Any] = {}

    def build_and_merge_data_region_query(self) -> pd.DataFrame:

        col_list_whole_data_body = [
            col for col in self.whole_data_body.columns if col not in self.default_list
        ]

        for i, c in enumerate(col_list_whole_data_body):
            self.flat_json_dict[f"{c}"] = self.whole_data_body[c]

        for i, element in enumerate(col_list_whole_data_body):
            self.query_data[f"data_0{i}"] = json_normalize(
                self.flat_json_dict[element][0]
            )
            try:
                self.query_data[f"data{i}"] = (
                    self.query_data[f"data_0{i}"]
                    .pivot(index="year", columns="type", values="value")
                    .reset_index()
                )
                cols = list(self.query_data[f"data{i}"].columns)
                new_cols = [
                    x.replace(
                        "GES",
                        col_list_whole_data_body[i].replace("data.region.", "")
                        + "_GES",
                    )
                    for x in cols
                ]
                self.query_data[f"data{i}"].columns = new_cols
            except KeyError:
                self.query_data[f"data{i}"] = self.query_data[f"data_0{i}"]
                cols = list(self.query_data[f"data{i}"].columns)
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
                self.query_data["data{}".format(i)].columns = new_cols

            self.query_data["data{}".format(i)]["id"] = (
                self.whole_data_body["data.region.id"][0]
                if "data.region.id" in self.whole_data_body.columns
                else None
            )
            self.query_data["data{}".format(i)]["name"] = (
                self.whole_data_body["data.region.name"][0]
                if "data.region.name" in self.whole_data_body.columns
                else None
            )

        data_out = self.query_data[f"data_0{0}"]
        for l, element in enumerate(col_list_whole_data_body[1:]):
            data_out["fake_id"] = 1
            self.query_data[f"data{l+1}"]["fake_id"] = 1
            data_out = data_out.merge(self.query_data[f"data{l+1}"], how="outer").drop(
                "fake_id", axis=1
            )

        return data_out

    def transform(self):
        output = self.build_and_merge_data_region_query()
        return output
