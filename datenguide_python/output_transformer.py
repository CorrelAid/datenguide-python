class QueryOutputTransformer:
    """ IN PROGRESS only region query to do: DOKU """

    def __init__(self):
        pass

    @staticmethod
    def flatten_query(dic):
        from pandas.io.json import json_normalize

        flat = json_normalize(dic)
        return flat

    @staticmethod
    def get_col_list(df):
        c = list(df.columns)
        c.remove("data.region.id")
        c.remove("data.region.name")
        return c

    @staticmethod
    def build_and_merge_data(dic, lis):
        import pandas as pd
        from pandas.io.json import json_normalize

        data = pd.DataFrame()
        for d in lis:
            try:
                if data.empty is True:
                    data = json_normalize(dic[d][0])
                    data.columns = [d, "year"]
                else:
                    temp = json_normalize(dic[d][0])
                    temp.columns = [d, "year"]
                    data = data.merge(temp, on="year", how="outer")
                print("no type variable")
            except ValueError:
                if data.empty is True:
                    data = json_normalize(dic[d][0])
                    newcolname = data.values[0][0] + "_" + d
                    data = data.iloc[:, 1:]
                    data.columns = [newcolname, "year"]
                else:
                    temp = json_normalize(dic[d][0])
                    newcolname = temp.values[0][0] + "_" + d
                    temp = temp.iloc[:, 1:]
                    temp.columns = [newcolname, "year"]
                    data = data.merge(temp, on="year", how="outer")
                print("type variable")
        newcol = [x.replace("data.region.", "") for x in data.columns]
        data.columns = newcol
        data["id"] = dic["data.region.id"][0]
        data["name"] = dic["data.region.name"][0]
        return data

    @staticmethod
    def drop_duplicates(df):
        data = df.drop_duplicates()
        return data

    @staticmethod
    def sort_by_year(df):
        data = df.sort_values("year")
        return data

    @staticmethod
    def order_cols(df):
        c = list(df.columns)
        for i in ["year", "id", "name"]:
            c.remove(i)
        cnew = ["id", "name", "year"] + c
        data = df[cnew]
        return data

    def transform(self, dic):
        flat = self.flatten_query(dic)
        c = self.get_col_list(flat)
        output = self.build_and_merge_data(flat, c)
        output = self.drop_duplicates(output)
        output = self.sort_by_year(output)
        output = self.order_cols(output)
        return output
