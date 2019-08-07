import pandas as pd

import numpy as np

from pandas.io.json import json_normalize


class QueryOutputTransformer:
    """ IN PROGRESS only region query to do: DOKU """

    def __init__(self):
        pass

    @staticmethod
    def flatten_query_result(dic):
        flat = json_normalize(dic)
        return flat

    @staticmethod
    def get_col_list(df):
        c = list(df.columns)
        try:
            c.remove("data.region.id")
        except ValueError:
            pass
        try:
            c.remove("data.region.name")
        except ValueError:
            pass
        return c

    @staticmethod
    def build_and_merge_data(dic, lis, year_default=True):
        data = json_normalize(dic[lis[0]][0])
        if year_default is True:
            data.columns = [lis[0], "year"]
            for d in lis[1:]:
                if json_normalize(dic[d][0]).empty is True:
                    temp = pd.DataFrame([np.nan, np.nan]).T
                    temp.columns = [d, "year"]
                elif json_normalize(dic[d][0]).empty is False:
                    temp = json_normalize(dic[d][0])
                    try:
                        temp.columns = [d, "year"]
                        print("no type variable")
                    except ValueError:
                        newcolname = temp.values[0][0] + "_" + d
                        temp = temp.iloc[:, 1:]
                        temp.columns = [newcolname, "year"]
                        print("type variable")
                data = data.merge(temp, on="year", how="outer")

            newcol = [x.replace("data.region.", "") for x in data.columns]
            data.columns = newcol
            try:
                data["id"] = dic["data.region.id"][0]
            except ValueError:
                pass
            try:
                data["name"] = dic["data.region.name"][0]
            except ValueError:
                pass

        if year_default is False:
            data.columns = [lis[0]]
            for d in lis[1:]:
                temp = json_normalize(dic[d][0])
                try:
                    temp.columns = [d]
                    print("no type variable")
                except ValueError:
                    newcolname = data.values[0][0] + "_" + d
                    temp = temp.iloc[:, 1:]
                    temp.columns = [newcolname]
                    print("type variable")
                pd.concat([data, temp], axis=1)

            newcol = [x.replace("data.region.", "") for x in data.columns]
            data.columns = newcol
            try:
                data["id"] = dic["data.region.id"][0]
            except ValueError:
                pass
            try:
                data["name"] = dic["data.region.name"][0]
            except ValueError:
                pass
        return data

    @classmethod
    def transform(cls, dic, year_default=True):
        flat = cls.flatten_query_result(dic)
        c = cls.get_col_list(flat)
        output = cls.build_and_merge_data(flat, c, year_default)
        return output
