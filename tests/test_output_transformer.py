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


@pytest.fixture
def query_results_with_enum():
    q = Query.region("09", default_fields=False)
    stat = q.add_field("WAHL09")
    stat.add_args({"PART04": "ALL"})
    stat.add_field("PART04")
    stat.add_field("year")
    stat.add_field("value")
    return QueryExecutioner().run_query(q)


def test_output_transformer_defaults(query_result):

    """ start test of output transformer """
    qOutTrans = QueryOutputTransformer(query_result)

    data_transformed = qOutTrans.transform()

    # test whether transformed output data is a dataframe
    assert type(data_transformed) == pd.DataFrame, "transformed data is not a dataframe"

    assert "id" in data_transformed.columns, "no id colum"
    assert "name" in data_transformed.columns, "no name colum"
    assert "year" in data_transformed.columns, "no year colum"
    assert "BEVMK3" in data_transformed.columns, "statistic values are missing"
    assert (
        "BEVMK3_value" not in data_transformed.columns
    ), "old statistics name still present"

    # columns of outdata should not contain json format
    lenlist = len(data_transformed.columns)
    checklist = ["." in data_transformed.columns[x] for x in range(lenlist)]
    assert not any(checklist), "hierarchy not properly transformed"


def test_output_transformer_format_options(query_result, query_results_with_enum):

    qOutTrans = QueryOutputTransformer(query_result)
    data_transformed = qOutTrans.transform(verbose_statistic_names=True)
    assert (
        "Von der Scheidung betroffene Kinder (BEVMK3)" in data_transformed.columns
    ), "statistic values are missing"

    enum_values = {
        "AFD",
        "B90_GRUENE",
        "CDU",
        "DIELINKE",
        "FDP",
        "SONSTIGE",
        "SPD",
        "GESAMT",
        None,
    }
    enum_descriptions = {
        "AfD",
        "GRÜNE",
        "CDU/CSU",
        "DIE LINKE",
        "FDP",
        "Sonstige Parteien",
        "SPD",
        "Gesamt",
    }

    qOutTrans = QueryOutputTransformer(query_results_with_enum)
    data_transformed = qOutTrans.transform()
    assert set(data_transformed["PART04"]).issubset(enum_values)

    qOutTrans = QueryOutputTransformer(query_results_with_enum)
    data_transformed = qOutTrans.transform(verbose_enum_values=True)
    assert set(data_transformed["PART04"]).issubset(enum_descriptions)

    qOutTrans = QueryOutputTransformer(query_results_with_enum)
    data_transformed = qOutTrans.transform(
        verbose_enum_values=True, verbose_statistic_names=True
    )
    assert "Gültige Zweitstimmen (WAHL09)" in data_transformed
