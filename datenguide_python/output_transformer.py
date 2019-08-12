import pandas as pd

import numpy as np

from pandas.io.json import json_normalize

from typing import List, Dict, Any


class QueryOutputTransformer:
    """ IN PROGRESS only region query to do: DOKU """

    def __init__(self):
        pass

    @staticmethod
    def get_col_list(df):
        c = [
            col
            for col in df.columns
            if col not in ["data.region.id", "data.region.name"]
        ]
        return c

    @staticmethod
    def build_and_merge_data(
        query_response_json: Dict[str, Any],
        some_fields: List[str],
        year_default: bool = True,
    ) -> pd.DataFrame:
        data = json_normalize(query_response_json[some_fields[0]][0])
        if year_default:
            data.columns = [some_fields[0], "year"]
            for d in some_fields[1:]:
                if json_normalize(query_response_json[d][0]).empty:
                    temp = pd.DataFrame([np.nan, np.nan]).T
                    temp.columns = [d, "year"]
                elif not json_normalize(query_response_json[d][0]).empty:
                    temp = json_normalize(query_response_json[d][0])
                    try:
                        temp.columns = [d, "year"]
                        print("no type variable")
                    except ValueError:
                        new_column_name = temp.iloc[0, 0] + "_" + d
                        temp = temp.iloc[:, 1:]
                        temp.columns = [new_column_name, "year"]
                        print("type variable")
                data = data.merge(temp, how="outer")

            newcol = [x.replace("data.region.", "") for x in data.columns]
            data.columns = newcol
            try:
                data["id"] = query_response_json["data.region.id"][0]
            except KeyError:
                pass
            try:
                data["name"] = query_response_json["data.region.name"][0]
            except KeyError:
                pass

        if not year_default:
            print(' "year" missing. query must contain "year"!')
            data = pd.DataFrame([])

        return data

    @classmethod
    def transform(cls, dic, year_default=True):
        flat = json_normalize(dic)
        c = cls.get_col_list(flat)
        output = cls.build_and_merge_data(flat, c, year_default)
        return output
