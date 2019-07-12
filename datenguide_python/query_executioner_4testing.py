import requests
import pandas as pd
import pprint
import requests

class QueryExecutioner:
    def __init__(self):
        pass
    
    def runQuery(self,queryString):
        post_json = dict()
        post_json["query"] = queryString
        header = { 'Content-Type': 'application/json' }
        URL = "https://api-next.datengui.de/graphql"
        resp = requests.post(url=URL,headers=header,json=post_json)

        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(f"Http error: status code {resp.status_code}")
