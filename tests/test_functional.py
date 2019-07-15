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
