from datenguide_python.query_execution import (
    QueryExecutioner,
    FieldMetaDict,
    TypeMetaData,
)

import pytest
from unittest.mock import Mock
from collections import namedtuple


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
    q1.get_fileds.return_value = ["region", "id", "name", "BEVMK3", "value", "year"]

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


@pytest.fixture
def type_request_response():
    request = Mock()
    expected_type_info = TypeMetaData(
        kind="ENUM",
        fields=None,
        enum_values={"R12631": "Statistik rechtskräftiger Urteile in Ehesachen"},
    )
    request.return_value = {
        "data": {
            "__type": {
                "kind": "ENUM",
                "name": "BEVMK3Statistics",
                "enumValues": [
                    {
                        "name": "R12631",
                        "description": "Statistik rechtskräftiger Urteile in Ehesachen",
                    }
                ],
                "fields": None,
            }
        }
    }
    return request, expected_type_info


@pytest.fixture
def sample_stat_meta_response():
    return {
        "id": FieldMetaDict(
            {"name": "id", "description": "Regionalschlüssel", "args": []}
        ),
        "name": FieldMetaDict({"name": "name", "description": "Name", "args": []}),
        "AENW01": FieldMetaDict(
            {
                "name": "AENW01",
                "description": "**Description 1** long additional description",
                "args": [
                    {
                        "name": "year",
                        "defaultValue": None,
                        "type": {
                            "kind": "LIST",
                            "name": None,
                            "ofType": {
                                "name": "Int",
                                "description": "LONG DESCRIPTION",
                                "kind": "SCALAR",
                            },
                        },
                    },
                    {
                        "name": "statistics",
                        "defaultValue": None,
                        "type": {
                            "kind": "LIST",
                            "name": None,
                            "ofType": {
                                "name": "AENW01Statistics",
                                "description": "",
                                "kind": "ENUM",
                            },
                        },
                    },
                ],
            }
        ),
        "AENW02": FieldMetaDict(
            {
                "name": "AENW02",
                "description": "Description 2",
                "args": [
                    {
                        "name": "year",
                        "defaultValue": None,
                        "type": {
                            "kind": "LIST",
                            "name": None,
                            "ofType": {
                                "name": "Int",
                                "description": "LONG DESCRIPTION",
                                "kind": "SCALAR",
                            },
                        },
                    },
                    {
                        "name": "statistics",
                        "defaultValue": None,
                        "type": {
                            "kind": "LIST",
                            "name": None,
                            "ofType": {
                                "name": "AENW02Statistics",
                                "description": "",
                                "kind": "ENUM",
                            },
                        },
                    },
                ],
            }
        ),
    }


@pytest.fixture
def stat_description():
    return (
        "**This md bold text should be extracted** everything else should not",
        "This md bold text should be extracted",
    )


def test_filter_stat_metatdata(sample_stat_meta_response):
    processed_stat_meta = QueryExecutioner._process_stat_meta_data(
        sample_stat_meta_response
    )
    assert all(
        all(("name" in stat, "description" in stat, "args" in stat))
        for stat in processed_stat_meta
    )
    assert all(
        any(arg["name"] == "statistics" for arg in field["args"])
        for field in processed_stat_meta
    )
    assert len(processed_stat_meta) == 2, "too many fields filtered out"


def test_generate_post_json(sample_queries):
    post_json = QueryExecutioner._generate_post_json(sample_queries.data_query1)
    sample_queries.data_query1.get_graphql_query.assert_called_once()
    assert "query" in post_json, "post jsons does not contain a query key"
    assert (
        post_json["query"] == sample_queries.data_query1.get_graphql_query.return_value
    ), "query not part of the post json"


def test_extract_stat_desc(stat_description):
    extracted_text = QueryExecutioner._extract_main_description(stat_description[0])
    assert (
        extracted_text == stat_description[1]
    ), "extracted text does not match bold part"


def test_create_stat_desc_dic(sample_stat_meta_response):
    desc_dict = QueryExecutioner._create_stat_desc_dic(sample_stat_meta_response)
    assert desc_dict["AENW01"] == "Description 1", "first dict entry is wrong"
    assert desc_dict["AENW02"] == "NO DESCRIPTION FOUND", "second dict entry is wrong"


def test_get_args(sample_stat_meta_response):
    args = sample_stat_meta_response["AENW01"].get_arguments()
    assert "year" in args, "year argument missing for AENW01"
    assert "statistics" in args, "statistic missing for AEW01"
    assert args["year"] == ("LIST", None, "SCALAR", "Int")
    assert args["statistics"] == ("LIST", None, "ENUM", "AENW01Statistics")


def test_get_type_info_caches_results(type_request_response):
    req_mock, expected_result = type_request_response
    qe = QueryExecutioner()
    qe._send_request = req_mock
    qe.__class__._META_DATA_CACHE = dict()  # clear cache
    assert (
        "BEVMK3Statistics" not in qe.__class__._META_DATA_CACHE
    ), "statistics should not be in cache"
    res = qe.get_type_info("BEVMK3Statistics")
    assert res == expected_result, "incorrect response processing"
    qe._send_request.assert_called_once()
    assert "BEVMK3Statistics" in qe.__class__._META_DATA_CACHE
    assert (
        qe.__class__._META_DATA_CACHE["BEVMK3Statistics"] == expected_result
    ), "cache results are wrong"


def test_get_type_info_uses_cached_resutls(type_request_response):
    req_mock, expected_result = type_request_response
    qe = QueryExecutioner()
    qe._send_request = req_mock
    qe.__class__._META_DATA_CACHE = {"BEVMK3Statistics": expected_result}
    res = qe.get_type_info("BEVMK3Statistics")
    assert res == expected_result
    qe._send_request.assert_not_called()
