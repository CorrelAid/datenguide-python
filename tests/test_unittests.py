from datenguide_python.query_execution import QueryExecutioner

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
def sample_stat_meta_response():
    return {
        "data": {
            "__type": {
                "fields": [
                    {"name": "id", "description": "Regionalschlüssel", "args": []},
                    {"name": "name", "description": "Name", "args": []},
                    {
                        "name": "AENW01",
                        "description": "**Description 1** long additional description",
                        "args": [{"name": "year"}, {"name": "statistics"}],
                    },
                    {
                        "name": "AENW02",
                        "description": "Description 2",
                        "args": [{"name": "year"}, {"name": "statistics"}],
                    },
                ]
            }
        }
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
