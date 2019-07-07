import requests
import pandas as pd
import pprint
import requests

class QueryOutputTransformer:
    """ source: https://github.com/KonradUdoHannes/datenguide-spike/blob/master/scribble.ipynb, 
     this version slightly adapted """

    def __init__(self):
        print(" in progress ")
    
    def countDataFrames(self, dic):
        n_dfs = 0
        for value in dic.values():
            if type(value) == pd.DataFrame:
                n_dfs += 1
        return n_dfs

    def findDataFrame(self, dic):
        for (key,value) in dic.items():
            if type(value) == pd.DataFrame:
                return value

    def addDictScalarsToDf(self, dic, df):
        for (key,value) in dic.items():
            if type(value) != pd.DataFrame:
                df[key] = value
            else:
                df = df.rename(columns = {'value':key})
        return df

    def dicToDf(self, dic):
        n_df = self.countDataFrames(dic)
        if n_df == 0:
            return pd.DataFrame(dic,index=[0])
        else:
            df = self.findDataFrame(dic)
            return self.addDictScalarsToDf(dic, df)

    def convertHirachy(self, dic):
        new_dic = dict()
        for key,value in dic.items():
            if type(value) == dict:
                new_dic[key] = self.convertHirachy(value)
            elif type(value) == list:
                new_dic[key] = pd.concat(list(map(self.convertHirachy,value)))
            else:
                new_dic[key] = value
        return self.dicToDf(new_dic)
    
    def transform(self, dic):
        output = self.convertHirachy(dic)
        return output