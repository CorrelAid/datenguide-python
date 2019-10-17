import pandas as pd
import pytest

from datenguidepy.output_transformer import QueryOutputTransformer
from datenguidepy.query_execution import QueryExecutioner
from datenguidepy.query_builder import Field, Query


@pytest.fixture
def query_result():
    field = Field(name="BEVMK3", fields=["value", "year"])
    query = Query.region(region="05911", fields=["id", "name", field])
    return QueryExecutioner().run_query(query)


def test_output_transformer(query_result):

    """ start test of output transformer """
    qOutTrans = QueryOutputTransformer(query_result)

    data_transformed = qOutTrans.transform()

    # test whether transformed output data is a dataframe
    assert type(data_transformed) == pd.DataFrame, "transformed data is not a dataframe"

    assert "id" in data_transformed.columns, "no id colum"
    assert "name" in data_transformed.columns, "no name colum"
    assert "year" in data_transformed.columns, "no year colum"

    # columns of outdata should not contain json format
    lenlist = len(data_transformed.columns)
    checklist = ["." in data_transformed.columns[x] for x in range(lenlist)]
    assert True not in checklist, "hierarchy not properly transformed"
