from datenguidepy.query_execution import QueryExecutioner, FieldMetaDict, TypeMetaData
from datenguidepy.output_transformer import QueryOutputTransformer
from datenguidepy.query_helper import get_statistics, get_all_regions, federal_states

import pytest
from unittest.mock import Mock
from collections import namedtuple
import pandas as pd


@pytest.fixture
def sample_queries():
    q1 = Mock()
    q1.get_graphql_query.return_value = [
        """
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
    ]
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
    post_jsons = QueryExecutioner._generate_post_json(sample_queries.data_query1)
    sample_queries.data_query1.get_graphql_query.assert_called_once()
    assert "query" in post_jsons[0], "post jsons does not contain a query key"
    assert (
        post_jsons[0]["query"]
        == sample_queries.data_query1.get_graphql_query.return_value[0]
    ), "query not part of the post json"


def test_extract_stat_desc(stat_description):
    extracted_text = QueryExecutioner._extract_main_description(stat_description[0])
    assert (
        extracted_text == stat_description[1]
    ), "extracted text does not match bold part"


def test_create_stat_desc_dic(sample_stat_meta_response):
    desc_dict = QueryExecutioner._create_stat_desc_dic(sample_stat_meta_response)
    assert desc_dict["AENW01"][0] == "Description 1", "first dict entry is wrong"
    assert (
        desc_dict["AENW02"][0] == "NO DESCRIPTION FOUND"
    ), "second dict entry is wrong"


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

    def test_QueryExecutionerWorkflow(sample_queries):
        qExec = QueryExecutioner()

        assert (
            qExec.endpoint == "https://api-next.datengui.de/graphql"
        ), "Default endpoint is wrong"

        res_query1 = qExec.run_query(sample_queries.data_query1)
        assert res_query1 is not None, "query did not return results"

        assert len(res_query1.query_results) > 0, "query did not return results"
        assert (
            type(res_query1.query_results) is dict
        ), "query results are not a python json representation"

        assert type(res_query1.meta_data) == dict, "meta data not a dict"
        assert len(res_query1.meta_data) > 0, "meta data absent"
        assert len(res_query1.meta_data) == 1, "too much meta data"

        assert "BEVMK3" in res_query1.meta_data, "statistic absend"
        assert (
            res_query1.meta_data["BEVMK3"] != "NO DESCRIPTION FOUND"
        ), "descrption was not obtained"

        info = qExec.get_type_info("Region")
        assert info.kind == "OBJECT", "Region should be an object"
        assert info.enum_values is None, "Region doesn't have enum values"
        assert type(info.fields) == dict, "Fields should be a dict"

        stat_args = info.fields["BEVMK3"].get_arguments()
        assert len(stat_args) > 0
        assert "statistics" in stat_args

        enum_vals = qExec.get_type_info("BEVMK3Statistics").enum_values
        assert type(enum_vals) == dict, "Enum values should be dict"
        assert len(enum_vals) > 0, "Enums should have values"


def test_federal_states():
    state_mappings = [
        ("Schleswig_Holstein", "01"),
        ("Hamburg", "02"),
        ("Niedersachsen", "03"),
        ("Bremen", "04"),
        ("Nordrhein_Westfalen", "05"),
        ("Hessen", "06"),
        ("Rheinland_Pfalz", "07"),
        ("Baden_Württemberg", "08"),
        ("Bayern", "09"),
        ("Saarland", "10"),
        ("Berlin", "11"),
        ("Brandenburg", "12"),
        ("Mecklenburg_Vorpommern", "13"),
        ("Sachsen", "14"),
        ("Sachsen_Anhalt", "15"),
        ("Thüringen", "16"),
    ]
    print(federal_states)
    for name, id in state_mappings:
        dic_id = getattr(federal_states, name)
        assert dic_id == id, f"{dic_id},{id}"


def test_regions_overview_table():
    reg = get_all_regions()
    assert isinstance(reg, pd.DataFrame)
    assert list(reg.columns) == ["name", "level", "parent"]
    assert reg.index.name == "id"
    assert reg.shape[0] > 10000


def test_statistic_overview_table():
    stats = get_statistics()
    assert isinstance(stats, pd.DataFrame)
    assert list(stats.columns) == [
        "statistics",
        "short_description",
        "long_description",
    ]
    assert stats.shape[0] > 400


def test_determine_column_order():
    input_columns = ["source_A", "source_B", "stat_A_value", "stat_B_value", "year"]
    input_frame = pd.DataFrame([], columns=input_columns)
    join_columns = set(["year"])

    output = QueryOutputTransformer._determine_column_order(input_frame, join_columns)
    expected_output = ["year", "stat_A_value", "stat_B_value", "source_A", "source_B"]

    assert output == expected_output


def test_prefix_frame_columns():
    cols = ["year", "stat_value", "source"]
    df = pd.DataFrame([], columns=cols)
    output = list(
        QueryOutputTransformer._prefix_frame_cols(
            df, prefix="A", exceptions=["year"]
        ).columns
    )
    expected_output = ["year", "A_stat_value", "A_source"]

    assert output == expected_output


def test_determine_join_columns():
    df_1 = pd.DataFrame(
        [], columns=["year", "source_detail1", "source_detail2", "value"]
    )
    df_2 = pd.DataFrame(
        [], columns=["year", "GES", "source_detail1", "source_detail2", "value"]
    )
    df_3 = pd.DataFrame(
        [], columns=["year", "source_detail1", "source_detail2", "value"]
    )
    frames_inp = [df_1, df_2, df_3]
    output = QueryOutputTransformer._determine_join_columns(frames_inp)
    expected_output = set(["year"])
    assert output == expected_output

    df_1 = pd.DataFrame(
        [], columns=["year", "NAT", "GES", "source_detail1", "source_detail2", "value"]
    )
    df_2 = pd.DataFrame(
        [], columns=["year", "GES", "source_detail1", "source_detail2", "value"]
    )
    frames_inp = [df_1, df_2]
    output = QueryOutputTransformer._determine_join_columns(frames_inp)
    expected_output = set(["year", "GES"])
    assert output == expected_output


def test_get_general_fields():
    meta_dict = {"stat_1": "stat_1 description", "stat_2": "stat_2 description"}
    region_json = {
        "id": "11",
        "stat_1": [],
        "name": "Berlin",
        "stat_2": [{"year": 2000, "value": 1}, {"year": 2001, "value": 2}],
    }
    output = QueryOutputTransformer._get_general_fields(region_json, meta_dict)
    expected_output = ["id", "name"]
    assert output == expected_output


def test_get_query_specific_stat_meta():
    field_type_list = [
        ("id", "String"),
        ("name", "String"),
        ("WAHL09", "WAHL09"),
        ("PART04", "PART04"),
        ("year", "Int"),
        ("value", "Float"),
    ]
    query_stat_meta = QueryExecutioner()._get_query_stat_meta(field_type_list)
    expected_stat_meta = {"WAHL09": "Gültige Zweitstimmen"}
    assert query_stat_meta == expected_stat_meta


def test_get_query_specific_enum_meta():
    field_type_list = [
        ("id", "String"),
        ("name", "String"),
        ("WAHL09", "WAHL09"),
        ("PART04", "PART04"),
        ("year", "Int"),
        ("value", "Float"),
    ]
    query_stat_meta = QueryExecutioner()._get_query_enum_meta(field_type_list)
    expected_stat_meta = {
        "PART04": dict(
            [
                ("AFD", "AfD"),
                ("B90_GRUENE", "GRÜNE"),
                ("CDU", "CDU/CSU"),
                ("DIELINKE", "DIE LINKE"),
                ("FDP", "FDP"),
                ("SONSTIGE", "Sonstige Parteien"),
                ("SPD", "SPD"),
                ("GESAMT", "Gesamt"),
            ]
        )
    }
    assert query_stat_meta == expected_stat_meta
