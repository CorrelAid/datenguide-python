import pandas as pd

from pandas.io.json import json_normalize

from typing import Dict, Any


class QueryOutputTransformer:
    """ IN PROGRESS only region query to do: DOKU """

    def __init__(self, query_response_json: Dict[str, Any]):
        """[summary]

        Arguments:
            query_response_json (Dict[str, Any]) -- [description]
        """
        self.whole_data_body = json_normalize(query_response_json, sep="_")
        self.query_data: Dict[str, Any] = {}
        self.default_list = ["data_region_id", "data_region_name"]
        self.flat_json_dict: Dict[str, Any] = {}

    def _build_and_merge_data_region_query(self) -> pd.DataFrame:

        col_list_whole_data_body = [
            col for col in self.whole_data_body.columns if col not in self.default_list
        ]

        for i, c in enumerate(col_list_whole_data_body):
            self.flat_json_dict[f"{c}"] = self.whole_data_body[c]

        for i, element in enumerate(col_list_whole_data_body):
            self.query_data[f"data_0{i}"] = json_normalize(
                self.flat_json_dict[element][0], sep="_"
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
                        col_list_whole_data_body[i].replace("data_region_", "")
                        + "_GES",
                    )
                    for x in cols
                ]
                self.query_data[f"data{i}"].columns = new_cols
            except KeyError:
                self.query_data[f"data{i}"] = self.query_data[f"data_0{i}"]
                cols = list(self.query_data[f"data{i}"].columns)
                cols_2 = [
                    col_list_whole_data_body[i].replace("data_region_", "") + "_" + x
                    for x in cols
                ]
                cols_3 = [
                    x.replace(
                        col_list_whole_data_body[i].replace("data_region_", "")
                        + "_year",
                        "year",
                    )
                    for x in cols_2
                ]
                new_cols = [x.replace("data_region_", "") for x in cols_3]
                self.query_data["data{}".format(i)].columns = new_cols

            self.query_data["data{}".format(i)]["id"] = (
                self.whole_data_body["data_region_id"][0]
                if "data_region_id" in self.whole_data_body.columns
                else None
            )
            self.query_data["data{}".format(i)]["name"] = (
                self.whole_data_body["data_region_name"][0]
                if "data_region_name" in self.whole_data_body.columns
                else None
            )

        data_out = self.query_data[f"data_0{0}"]
        for l, element in enumerate(col_list_whole_data_body[1:]):
            data_out["fake_id"] = 1
            self.query_data[f"data{l+1}"]["fake_id"] = 1
            data_out = data_out.merge(self.query_data[f"data{l+1}"], how="outer").drop(
                "fake_id", axis=1
            )
        cols_4 = [col for col in data_out.columns if "_value" in col]
        cols_5 = ["id", "name", "year"] + cols_4
        cols_6 = [col for col in data_out.columns if col not in cols_5]
        output_ordered = data_out.loc[:, cols_5 + cols_6]
        cols_7 = [x.replace("_value", "") for x in output_ordered.columns]
        output_ordered.columns = cols_7

        return output_ordered

    def transform(self) -> pd.DataFrame:
        """Transform the queries results into a Pandas DataFrame.

        Returns:
            DataFrame -- Returns a pandas DataFrame of the queries results.
        """
        output = self._build_and_merge_data_region_query()
        return output
