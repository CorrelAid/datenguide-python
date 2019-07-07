import requests
import pandas as pd
import pprint
import requests

class QueryBuilder:
    def __init__(self):
        print("hi")
    
    def buildQuery(self):
        testquery = """
                          {
              region(id: "05911") {
                id
                name
                    BEVMK3 {
                value
                year
                }
              }
            }              
            """
        return testquery