import pandas

from datenguide_python.output_transformer import QueryOutputTransformer

from datenguide_python.query_executioner_4testing import QueryExecutioner

from datenguide_python.query_builder_4testing import QueryBuilder


def test_output_transformer():

    """ prepare test of output transformer """

    qBuild = QueryBuilder()
    testquery = qBuild.buildQuery()

    qExec = QueryExecutioner()
    query_result = qExec.runQuery(testquery)

    """ start test of output transformer """
    qOutTrans = QueryOutputTransformer()

    # test whether input data arrive in correct format
    assert type(query_result) == dict, "input data not dict type"

    data_transformed = qOutTrans.transform(query_result)

    # test whether transformed output data is a dataframe
    assert (
        type(data_transformed) == pandas.DataFrame
    ), "transformed data is not a dataframe"

    # outdata must contain 'id' column
    assert "id" in data_transformed.columns, "no id colum"

    # outdata must contain 'name' column
    assert "name" in data_transformed.columns, "no name colum"

    # outdata must contain 'year' column
    assert "year" in data_transformed.columns, "no year colum"

    # columns of outdata should not contain json format
    lenlist = len(data_transformed.columns)
    checklist = ["." in data_transformed.columns[x] for x in range(lenlist)]
    assert True not in checklist, "hierarchy not properly transformed"

    # outdata should not contain duplicates
    assert len(data_transformed.drop_duplicates()) == len(
        data_transformed
    ), "transformed data contain duplicates"

    # check year ranges
    assert (
        data_transformed["year"].min() > 1900
    ), "transformed data contain data from 1900 or before"
    assert (
        data_transformed["year"].max() < 2050
    ), "transformed data contain data from after 2050"
