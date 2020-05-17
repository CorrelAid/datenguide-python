import pytest
import re
import sys
import io
import pandas as pd
from datenguidepy import Field, Query
from datenguidepy.query_execution import (
    FieldMetaDict,
    TypeMetaData,
    GraphQlSchemaMetaDataProvider,
)


@pytest.fixture
def mock_graphqlschemaprovider(monkeypatch):
    def mock_meta_data(self, return_type):
        type_kind = "OBJECT"
        enum_vals = None
        if return_type == "Region":
            field_meta = {
                "id": FieldMetaDict(
                    {
                        "name": "id",
                        "type": {
                            "ofType": None,
                            "kind": "SCALAR",
                            "name": "String",
                            "description": "The `String` scalar type ...",
                        },
                        "description": "Regionalschlüssel",
                        "args": [],
                    }
                ),
                "name": FieldMetaDict(
                    {
                        "args": [],
                        "description": "Name",
                        "name": "name",
                        "type": {
                            "description": "The `String` scalar...",
                            "kind": "SCALAR",
                            "name": "String",
                            "ofType": None,
                        },
                    }
                ),
                "BEV001": FieldMetaDict(
                    {
                        "name": "BEV001",
                        "type": {
                            "ofType": {"name": "BEV001"},
                            "kind": "LIST",
                            "name": None,
                            "description": None,
                        },
                        "description": "Statistik der Geburten",
                        "args": [
                            {
                                "name": "year",
                                "type": {
                                    "kind": "LIST",
                                    "name": None,
                                    "ofType": {
                                        "name": "Int",
                                        "description": "The `Int` scalar type ...",
                                        "kind": "SCALAR",
                                    },
                                },
                            },
                            {
                                "name": "NAT",
                                "type": {
                                    "kind": "LIST",
                                    "name": None,
                                    "ofType": {
                                        "name": "NAT",
                                        "description": "Nationalität",
                                        "kind": "ENUM",
                                    },
                                },
                            },
                        ],
                    }
                ),
            }
        elif return_type == "BEV001":
            field_meta = {
                "id": FieldMetaDict(
                    {
                        "name": "id",
                        "type": {
                            "ofType": None,
                            "kind": "SCALAR",
                            "name": "String",
                            "description": "The `String` scalar...",
                        },
                        "description": "Interne eindeutige ID",
                        "args": [],
                    }
                ),
                "year": FieldMetaDict(
                    {
                        "args": [...],
                        "description": "Jahr des Stichtages",
                        "name": "year",
                        "type": {
                            "description": "The `Int` scalar...",
                            "kind": "SCALAR",
                            "name": "Int",
                            "ofType": None,
                        },
                    }
                ),
                "value": FieldMetaDict(
                    {
                        "args": [...],
                        "description": "Wert",
                        "name": "value",
                        "type": {
                            "description": "The `Float` scalar ...",
                            "kind": "SCALAR",
                            "name": "Float",
                            "ofType": None,
                        },
                    }
                ),
                "NAT": FieldMetaDict(
                    {
                        "args": [...],
                        "description": "Nationalität",
                        "name": "NAT",
                        "type": {
                            "description": "",
                            "kind": "ENUM",
                            "name": "NAT",
                            "ofType": None,
                        },
                    }
                ),
            }
        elif return_type == "NAT":
            type_kind = "ENUM"
            field_meta = None
            enum_vals = {
                "NAA": "Ausländer(innen)",
                "NAD": "Deutsche",
                "GESAMT": "Gesamt",
            }

        else:
            raise RuntimeError("return type not in Monkeypatch")

        return TypeMetaData(type_kind, field_meta, enum_vals)

    monkeypatch.setattr(GraphQlSchemaMetaDataProvider, "get_type_info", mock_meta_data)


@pytest.fixture
def field_default():
    return Field("WAHL09", args={"year": 2017}, fields=["PART04"], return_type="WAHL09")


@pytest.fixture
def query_default():
    return Query.region(region="09", fields=["BEV001"])


@pytest.fixture
def query_with_enum():
    q = Query.region("09", default_fields=False)
    stat = q.add_field("WAHL09")
    stat.add_field("PART04")
    stat.add_field("year")
    stat.add_field("value")
    return q


@pytest.fixture
def field():
    return Field(
        "WAHL09",
        args={"year": 2017},
        fields=["value", "year", "PART04"],
        default_fields=False,
        return_type="WAHL09",
    )


@pytest.fixture
def query():
    return Query.region(region="09", fields=["BEV001"], default_fields=False)


@pytest.fixture
def all_regions_query(field):
    return Query.all_regions(
        parent="11", fields=["id", "name", field], default_fields=False
    )


@pytest.fixture
def complex_query(field):
    return Query.region(region="09", fields=["id", "name", field], default_fields=False)


@pytest.fixture
def more_complex_query(complex_query):
    query = complex_query
    source = Field("source", fields=["title_de"], return_type="Source")
    statistic2 = Field(
        name="BEV001",
        args={"statistics": "R12612"},
        fields=["value", "year", source],
        default_fields=False,
    )
    query.add_field(statistic2)
    return query


def test_get_all_stats_info():
    info = Query.all_regions().get_info()
    assert "name" in info.fields


def test_get_field_info():
    info = Query.all_regions().get_info("BEV001")
    assert "BEVM01" in info.fields


def test_process_query(query_default):
    df = query_default.results()
    assert isinstance(df, pd.DataFrame)


def test_arguments_info_mocked(mock_graphqlschemaprovider, query):
    stat = query.add_field("BEV001")
    info = stat.arguments_info()
    expected_info = """\x1b[4myear\x1b[0m: LIST of type SCALAR(Int)

    \x1b[4mNAT\x1b[0m: LIST of type ENUM(NAT)
    enum values:
    NAA: Ausländer(innen)
    NAD: Deutsche
    GESAMT: Gesamt"""

    assert re.sub(r"\s+", "", info) == re.sub(r"\s+", "", expected_info)


def test_field_info_mocked(mock_graphqlschemaprovider, query):
    stat = query.add_field("BEV001")
    info = stat.fields_info()
    expected_info = """
    id: Interne eindeutige ID
    year: Jahr des Stichtages
    value: Wert
    NAT: Nationalität
    """
    assert re.sub(r"\s+", "", info) == re.sub(r"\s+", "", expected_info)


def test_description_mocked(mock_graphqlschemaprovider, query):
    stat = query.add_field("BEV001")
    descr = stat.description()
    assert descr == "Lebend Geborene"


def test_enum_mocked(mock_graphqlschemaprovider, query):
    stat = query.add_field("BEV001").add_field("NAT")
    info = stat.enum_info()
    expected_info = """
    NAA: Ausländer(innen)
    NAD: Deutsche
    GESAMT: Gesamt"""

    assert re.sub(r"\s+", "", info) == re.sub(r"\s+", "", expected_info)


def test_get_info_stat_mocked(mock_graphqlschemaprovider, query):
    stringio = io.StringIO()
    sys.stdout = stringio
    stat = query.add_field("BEV001")
    stat.get_info()
    info = stringio.getvalue()
    expected_info = """\x1b[1mkind:\x1b[0m
        OBJECT

        \x1b[1mdescription:\x1b[0m
        Lebend Geborene

        \x1b[1marguments:\x1b[0m
        \x1b[4myear\x1b[0m: LIST of type SCALAR(Int)

        \x1b[4mNAT\x1b[0m: LIST of type ENUM(NAT)
        enum values:
        NAA: Ausländer(innen)
        NAD: Deutsche
        GESAMT: Gesamt

        \x1b[1mfields:\x1b[0m
        id: Interne eindeutige ID
        year: Jahr des Stichtages
        value: Wert
        NAT: Nationalität

        \x1b[1menum values:\x1b[0m
        None"""

    assert re.sub(r"\s+", "", info) == re.sub(r"\s+", "", expected_info)


def test_get_fields_with_return_type(field, query_with_enum):
    fields_and_types = field._get_fields_with_types()
    expected_fields_and_types = set(
        [
            ("WAHL09", "WAHL09"),
            ("value", "Float"),
            ("year", "Int"),
            ("PART04", "PART04"),
        ]
    )
    assert set(fields_and_types) == expected_fields_and_types

    fields_and_types = query_with_enum._get_fields_with_types()
    expected_fields_and_types = set(
        [
            ("WAHL09", "WAHL09"),
            ("region", "Region"),
            ("value", "Float"),
            ("year", "Int"),
            ("PART04", "PART04"),
        ]
    )
    assert set(fields_and_types) == expected_fields_and_types
