import pytest
import pandas as pd
import sys
import io
import re
from datenguidepy.query_execution import QueryExecutioner
from datenguidepy.query_builder import Query, Field
from datenguidepy.query_helper import (
    federal_states,
    get_statistics,
    get_all_regions,
    download_all_regions,
)
from datenguidepy.output_transformer import QueryOutputTransformer


@pytest.fixture
def query():
    field = Field(name="BEVMK3", fields=["value", "year"])
    query = Query.region(region="05911", fields=["id", "name", field])
    return query


@pytest.fixture
def query_multi_regions():
    field = Field(name="BEVMK3", fields=["value", "year"])
    query = Query.region(region=["01", "02"], fields=["id", "name", field])
    return query


@pytest.fixture
def query_all_regions():
    field = Field(name="BEVMK3", fields=["value", "year"])
    query = Query.all_regions(nuts=1, fields=["id", "name", field])
    return query


def test_QueryExecutionerWorkflow(query):
    """Functional test for the query executioner"""

    # Ira (W. Cotton, probably the first person to use the term API) want to
    # try the query execution part of the datenguide GraphQL wrapper library.
    # He already worked through Query builder objects ready for execution.
    # He understands that he first has to create an executioner object that
    # it uses the right by default, so that he does not have to supply any
    # parameters.

    q_exec = QueryExecutioner()

    # After creating the object Ira is actually a little sceptical whether
    # the endpoint will correct so he extracts the endpoint and compares it
    # with his expectations.

    assert (
        q_exec.endpoint == "https://api-next.datengui.de/graphql"
    ), "Default endpoint is wrong"

    # Being satisfied that everything is setup with the correct endpoint Ira
    # now wants to execute one of his queries to see that he gets some return
    # values.

    res_query1 = query.results()

    assert res_query1 is not None, "query did not return results"

    # He wants to have a closer look at the raw return query results and
    # remembers that they are sorted in the results field and he has a look.

    assert (
        type(res_query1) is pd.DataFrame
    ), "query results are not a python json representation"

    stats = Query.get_info()

    # Ira remembers that he read about the executioners functionality to
    # return metadata along with the query results. So he wants to check
    # whether this metadata is actually present. And that it only contains
    # meta data related to his query

    meta_query1 = query.meta_data()

    # In particular Ira would like to have a more human readable description
    # of the statistic he asked for.

    assert "BEVMK3" in meta_query1["statistics"], "statistic absend"
    assert (
        meta_query1["statistics"]["BEVMK3"] != "NO DESCRIPTION FOUND"
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

    stringio = io.StringIO()
    sys.stdout = stringio

    statistic1.get_info()
    stats_info = re.sub(r"\n", "", stringio.getvalue())
    assert "OBJECT" in stats_info, "BEV001 should be an object"


def test_queryHelper():
    # Ira is happy with the functionality so far but is worried a bit
    # about the difficuilty of finding the right technichal ids for regions
    # and statistics.

    # He realizes that there is helper functionality to identify the
    # federal states quickly in a human readable way and wants to try
    # it for Berlin
    assert federal_states.Berlin == "11"

    # That already worked nicely but in general there are many regions.
    # Ira would like to easily search through all of them and realizes
    # that he can obtain a DataFrame for this.
    reg_locally_stored = get_all_regions()
    assert isinstance(reg_locally_stored, pd.DataFrame)

    # Ira reads in the help that this is a stored list of regions and
    # not obtained live from datenguide.
    # He knows that region definitions and ids don't change very
    # often, but he would like the ability to obtain the most up to date
    # regions anyways. He therefore tries the function download_all_regions
    # that is designed for this purpouse

    reg = download_all_regions()
    assert isinstance(reg, pd.DataFrame)
    assert list(reg.columns) == ["name", "level", "parent"]
    assert reg.index.name == "id"
    assert reg.shape[0] > 10000

    # Being satisfied with the regions, Ira now wants to have a
    # look at an equivalent overview of statistics.

    statistics = get_statistics()
    assert isinstance(statistics, pd.DataFrame)

    # Although this might already be sufficient for finding
    # interesting statistics, Ira read that there is already
    # some basic build in search functionality which
    # he wants to try.

    filtered_statistics = get_statistics("scheidung")
    assert isinstance(filtered_statistics, pd.DataFrame)
    assert filtered_statistics.shape[0] < 50


def test_build_execute_transform_integration(query):
    """
    Smoke test covering region query.
    """

    q_exec = QueryExecutioner()

    res = q_exec.run_query(query)

    output_transf = QueryOutputTransformer(res)
    output_transf.transform()


def test_build_execute_transform_integration_multi_region(query_multi_regions):
    """
    Smoke test covering multiple regions in
    region query.
    """

    q_exec = QueryExecutioner()

    res = q_exec.run_query(query_multi_regions)

    output_transf = QueryOutputTransformer(res)
    output_transf.transform()


def test_build_execute_transform_integration_all_regions(query_all_regions):
    """
    Smoke test covering all_regions
    """
    q_exec = QueryExecutioner()

    res = q_exec.run_query(query_all_regions)

    output_transf = QueryOutputTransformer(res)
    output_transf.transform()
