import pandas

import requests

from datenguidepy.output_transformer import QueryOutputTransformer


def buildQuery():
    testquery = """
                          {
              region(id: "05911") {
                id
                name
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


def runQuery(queryString):

    post_json = dict()
    post_json["query"] = queryString
    header = {"Content-Type": "application/json"}
    URL = "https://api-next.datengui.de/graphql"
    resp = requests.post(url=URL, headers=header, json=post_json)

    if resp.status_code == 200:
        return resp.json()
    else:
        raise Exception(f"Http error: status code {resp.status_code}")


def test_output_transformer():

    """ prepare test of output transformer """

    testquery = buildQuery()

    query_result = runQuery(testquery)

    """ start test of output transformer """
    qOutTrans = QueryOutputTransformer(query_result)

    # test whether input data arrive in correct format
    assert type(query_result) == dict, "input data not dict type"

    data_transformed = qOutTrans.transform()

    # test whether transformed output data is a dataframe
    assert (
        type(data_transformed) == pandas.DataFrame
    ), "transformed data is not a dataframe"

    assert "id" in data_transformed.columns, "no id colum"
    assert "name" in data_transformed.columns, "no name colum"
    assert "year" in data_transformed.columns, "no year colum"

    # columns of outdata should not contain json format
    lenlist = len(data_transformed.columns)
    checklist = ["." in data_transformed.columns[x] for x in range(lenlist)]
    assert True not in checklist, "hierarchy not properly transformed"
