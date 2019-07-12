import requests
import pandas as pd
import pprint
import requests
from pandas.io.json import json_normalize

class QueryOutputTransformer:
    # test only region query
    def __init__(self):
        pass
    
    def flatten_query(self, dic):
        flat = json_normalize(dic)
        return flat

    def get_col_list(self, df):
        c = list(df.columns)
        c.remove('data.region.id')
        c.remove('data.region.name')
        return c

    def build_and_merge_data(self, dic, lis):
        data = pd.DataFrame()
        for d in lis:
            if data.empty == True:
                data = json_normalize(dic[d][0])
                data.columns = [d, 'year']
            else:
                temp = json_normalize(dic[d][0])
                temp.columns = [d, 'year']
                data = data.merge(temp, on='year', how='outer')
        newcol = [x.replace('data.region.', '') for x in data.columns]
        data.columns = newcol
        data['id'] = dic['data.region.id'][0]
        data['name'] = dic['data.region.name'][0]
        return data

    def drop_duplicates(self, df):
        data = df.drop_duplicates()
        return data
    
    def sort_by_year(self, df):
        data = df.sort_values('year')
        return data

    def order_cols(self, df):
        c=list(df.columns)
        for i in ['year', 'id', 'name']: c.remove(i)
        cnew = ['id','name','year'] + c
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