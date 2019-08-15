import pandas

import requests

from datenguide_python.output_transformer import QueryOutputTransformer


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

    metadata = {"id": "09"}

    """ start test of output transformer """
    qOutTrans = QueryOutputTransformer()

    # test whether input data arrive in correct format
    assert type(query_result) == dict, "input data not dict type"

    data_transformed = qOutTrans.transform(query_result, metadata)

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

    # outdata should not contain duplicates
    # assert len(data_transformed.drop_duplicates()) == len(
    #    data_transformed
    # ), "transformed data contain duplicates"

    # check year ranges
    # assert (
    #    data_transformed["year"].min() > 1900
    # ), "transformed data contain data from 1900 or before"
    # assert (
    #    data_transformed["year"].max() < 2050
    # ), "transformed data contain data from after 2050"
