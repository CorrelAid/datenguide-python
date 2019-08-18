import pytest


from datenguide_python.query_execution import QueryExecutioner
from datenguide_python.query_builder import Query, Field


@pytest.fixture
def query():
    field = Field(name="BEVMK3", fields=["value", "year"])
    query = Query.regionQuery(region="05911", fields=["id", "name", field])
    return query


def test_QueryExecutionerWorkflow(query):
    """Functional test for the query executioner"""

    # Ira (W. Cotton, probably the first person to use the term API) want to
    # try the query execution part of the datenguide GraphQL wrapper library.
    # He already worked through Query builder objects ready for execution.
    # He understands that he first has to create an executioner object that
    # it uses the right by default, so that he does not have to supply any
    # parameters.

    qExec = QueryExecutioner()

    # After creating the object Ira is actually a little sceptical whether
    # the endpoint will correct so he extracts the endpoint and compares it
    # with his expectations.

    assert (
        qExec.endpoint == "https://api-next.datengui.de/graphql"
    ), "Default endpoint is wrong"

    # Being satisfied that everything is setup with the correct endpoint Ira
    # now wants to execute one of his queries to see that he gets some return
    # values.

    res_query1 = query.results()

    assert res_query1 is not None, "query did not return results"

    # He wants to have a closer look at the raw return query results and
    # remembers that they are sorted in the results field and he has a look.

    assert len(res_query1.query_results) > 0, "query did not return results"
    assert (
        type(res_query1.query_results) is dict
    ), "query results are not a python json representation"

    # Ira wants to get an overview of all possible statistics that can be
    # queried.

    stats = Query.get_info()
    assert stats.kind == "OBJECT", "Region should be an object"
    assert stats.enum_values is None, "Region doesn't have enum values"
    assert type(stats.fields) == dict, "Fields should be a dict"

    # Ira remembers that he read about the executioners functionality to
    # return metadata along with the query results. So he wants to check
    # whether this metadata is actually present. And that it only contains
    # meta data related to his query

    assert type(res_query1.meta_data) == dict, "meta data not a dict"
    assert len(res_query1.meta_data) > 0, "meta data absent"
    assert len(res_query1.meta_data) == 1, "too much meta data"

    # In particular Ira would like to have a more human readable description
    # of the statistic he asked for.

    assert "BEVMK3" in res_query1.meta_data, "statistic absend"
    assert (
        res_query1.meta_data["BEVMK3"] != "NO DESCRIPTION FOUND"
    ), "descrption was not obtained"

    # Being satisfied with the results he obtained for his simple query
    # he actually wants to try a larger one across several regions. He heard
    # that this might be an issue for the server in general, but that the
    # executioner takes care of addressing this issue by itself.

    # Since this is a lot of information Ira would particularly
    # like to drill down on the arguments that are allowed for his
    # favorite statistic BEVMK3

    stat_args = stats.fields["BEVMK3"].get_arguments()
    assert len(stat_args) > 0
    assert "statistics" in stat_args

    # Although this is already really helpful Ira notices that
    # one of the arguments is an ENUM and he would like to know
    # the possible values that he can use for it.

    enum_vals = Query.get_info("BEVMK3Statistics").enum_values
    assert type(enum_vals) == dict, "Enum values should be dict"
    assert len(enum_vals) > 0, "Enums should have values"

    # Ira wants to add another statistic to his query.
    statistic1 = query.add_field("BEV001")
    statistic1.add_field("year")
    statistic1.add_args({"year": 2017})

    assert type(statistic1) == Field, "statistic is not a Field"

    # Then he wants to get metainfo on the field.

    stats_info = statistic1.get_info()
    assert stats_info.kind == "OBJECT", "BEV001 should be an object"
    assert type(stats_info.fields) == dict, "Fields should be a dict"
