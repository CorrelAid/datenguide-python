from unittest.mock import Mock
from collections import namedtuple
import pytest


from datenguide_python.query_execution import QueryExecutioner


@pytest.fixture
def sample_queries():
    q1 = Mock()
    q1.get_graphql_query.return_value = """
    {
        region(id:"05911") {
            id
            name
            BEVMK3 {
                value
                year
            }
        }
    }
    """
    q1.get_fields.return_value = ["region", "id", "name", "BEVMK3", "value", ".year"]

    mq1 = Mock()
    mq1.get_graphql_query.return_value = """
    {
      __type(name: "Region") {
        name
        fields {
          name
          description
          type {
            name
            kind
          }
        }
      }
    }
    """
    SampleQueries = namedtuple("SampleQueries", "data_query1 meta_query1")
    return SampleQueries(q1, mq1)


def test_QueryExecutionerWorkflow(sample_queries):
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

    res_query1 = qExec.run_query(sample_queries.data_query1)
    assert res_query1 is not None, "query did not return results"

    # He wants to have a closer look at the raw return query results and
    # remembers that they are sorted in the results field and he has a look.

    assert len(res_query1.query_results) > 0, "query did not return results"
    assert (
        type(res_query1.query_results) is dict
    ), "query results are not a python json representation"

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

    # IMPLEMENT ON QUERY BUILDER SIDE?

    # so far everything has been quite nice but Ira feels a little
    # lost with all the types and arguments. But he knows that the
    # executioner can actually give information on types and Ira
    # happens to know that the type of region queries is "Region"
    # and he tries to gen info on it.

    info = qExec.get_type_info("Region")
    assert info.kind == "OBJECT", "Region should be an object"
    assert info.enum_values is None, "Region doesn't have enum values"
    assert type(info.fields) == dict, "Fields should be a dict"

    # Since this is a lot of information Ira would particularly
    # like to drill down on the arguments that are allowed for his
    # favorite statistic BEVMK3

    stat_args = info.fields["BEVMK3"].get_arguments()
    assert len(stat_args) > 0
    assert "statistics" in stat_args

    # Although this is already really helpfull Ira notices that
    # one of the arguments is an ENUM and he would like to know
    # the possible values that he can use for it.

    enum_vals = qExec.get_type_info("BEVMK3Statistics").enum_values
    assert type(enum_vals) == dict, "Enum values should be dict"
    assert len(enum_vals) > 0, "Enums should have values"
