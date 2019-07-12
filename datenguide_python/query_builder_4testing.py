import requests
import pandas as pd
import pprint
import requests

class QueryBuilder:
    def __init__(self):
        pass
    
    def buildQuery(self):
        testquery = """
                          {
              region(id: "05911") {
                id
                name
                BEVZ20(statistics: R12111, filter: { GES: { in: ["GESM", "GESM"]} }) {
                type: GES
                year
                value
                }
                AI0101 {
                value
                year
                }
                AENW01 {
                value
                year
                }
                BEV083 {
                value
                year
                }
                BEVSTD {
                value
                year
                }
                BEVMK3 {
                value
                year
                }
              }
            }              
            """
        return testquery