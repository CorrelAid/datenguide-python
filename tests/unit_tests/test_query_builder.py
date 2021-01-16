import pytest
import re
from datenguidepy import Field, Query
from datenguidepy.query_execution import FieldMetaDict


@pytest.fixture
def patch_return_types(monkeypatch):
    def field_construction_return_types(self, fieldname):
        essential_types = {"year": "Int", "value": "Float", "source": "Source"}
        return essential_types.get(fieldname, "NOT IN MONKEYPATCH")

    monkeypatch.setattr(Field, "_get_return_type", field_construction_return_types)


@pytest.fixture
def mocked_enum_placeholder(monkeypatch):
    def mocked_enum_placeholder(self):
        return "MOCKED ENUM VALUES"

    monkeypatch.setattr(Field, "enum_info", mocked_enum_placeholder)


@pytest.fixture
def mocked_arguments():
    return {
        "WAHL09": FieldMetaDict(
            {
                "name": "WAHL09",
                "type": {
                    "ofType": {"name": "WAHL09"},
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
        )
    }


@pytest.fixture
def meta_fields():
    field_meta = {
        "id": {
            "name": "id",
            "type": {
                "ofType": None,
                "kind": "SCALAR",
                "name": "String",
                "description": "The `String` scalar...",
            },
            "description": "Interne eindeutige ID",
            "args": [],
        },
        "year": {
            "name": "year",
            "type": {
                "ofType": None,
                "kind": "SCALAR",
                "name": "Int",
                "description": "The `Int`...",
            },
            "description": "Jahr des Stichtages",
            "args": [],
        },
        "value": {
            "name": "value",
            "type": {
                "ofType": None,
                "kind": "SCALAR",
                "name": "Float",
                "description": "The `Float`...",
            },
            "description": "Wert",
            "args": [],
        },
        "source": {
            "name": "source",
            "type": {
                "ofType": None,
                "kind": "OBJECT",
                "name": "Source",
                "description": "",
            },
            "description": "Quellenverweis zur GENESIS Regionaldatenbank",
            "args": [],
        },
        "PART04": {
            "name": "PART04",
            "type": {
                "ofType": None,
                "kind": "ENUM",
                "name": "PART04",
                "description": "Parteien",
            },
            "description": "Parteien",
            "args": [],
        },
    }
    return field_meta


@pytest.fixture
def enum_input():
    return {"NATA": "Ausländer(innen)", "NATD": "Deutsche", "GESAMT": "Gesamt"}


@pytest.fixture
def field_default(patch_return_types):
    return Field("WAHL09", args={"year": 2017}, fields=["PART04"], return_type="WAHL09")


@pytest.fixture
def query_default(patch_return_types):
    return Query.region(region="09", fields=["BEV001"])


@pytest.fixture
def query_with_enum(patch_return_types):
    q = Query.region("09", default_fields=False)
    stat = q.add_field("WAHL09")
    stat.add_field("PART04")
    stat.add_field("year")
    stat.add_field("value")
    return q


@pytest.fixture
def field(patch_return_types):
    return Field(
        "WAHL09",
        args={"year": 2017},
        fields=["value", "year", "PART04"],
        default_fields=False,
        return_type="WAHL09",
    )


@pytest.fixture
def query(patch_return_types):
    return Query.region(region="09", fields=["BEV001"], default_fields=False)


@pytest.fixture
def all_regions_query(field, patch_return_types):
    return Query.all_regions(
        parent="11", fields=["id", "name", field], default_fields=False
    )


@pytest.fixture
def complex_query(field, patch_return_types):
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


def test_create_query_is_class_query(query):
    assert isinstance(query, Query)


def test_create_query_class_without_start_filed_raises_error():
    with pytest.raises(TypeError):
        Query()


def test_basic_graphql_string(query):
    graphql_query = query.get_graphql_query()
    assert graphql_query[0] == re.sub(
        " +", " ", """{region (id: "09"){BEV001 }}""".replace("\n", " ")
    )


def test_get_fields_to_query(patch_return_types):
    field = Field(
        name="WAHL09",
        args={"year": 2017},
        fields=["value", "PART04"],
        default_fields=False,
    )
    subfields_string = field._get_fields_to_query(field)
    assert subfields_string == "WAHL09 (year: 2017){value PART04 }"


def test_get_complex_graphql_string(complex_query):
    graphql_query = complex_query.get_graphql_query()
    assert graphql_query[0] == re.sub(
        "    ",
        "",
        """{
            region (id: "09"){
                id name WAHL09 (year: 2017){value year PART04 }
                }
            }""".replace(
            "\n", ""
        ),
    )


def test_get_complex_graphql_string_without_args(patch_return_types):
    field = Field(name="WAHL09", fields=["value"], default_fields=False)
    no_args_query = Query.region(
        region="09", fields=["id", "name", field], default_fields=False
    )

    graphql_query = no_args_query.get_graphql_query()
    assert graphql_query[0] == re.sub(
        "    ",
        "",
        """{
        region (id: "09"){
            id name WAHL09 {value }}
            }""".replace(
            "\n", ""
        ),
    )


def test_get_multiple_stats(more_complex_query):
    graphql_query = more_complex_query.get_graphql_query()
    assert graphql_query[0] == re.sub(
        "    ",
        "",
        """{
        region (id: "09"){
            id name WAHL09 (year: 2017){value year PART04 }
            BEV001 (statistics: R12612){value year source {title_de }}}
        }""".replace(
            "\n", ""
        ),
    )


def test_get_all_fields(query):
    assert query.get_fields() == ["region", "BEV001"]


def test_get_all_fields_complex(more_complex_query):
    assert more_complex_query.get_fields() == [
        "region",
        "id",
        "name",
        "WAHL09",
        "value",
        "year",
        "PART04",
        "BEV001",
        "value",
        "year",
        "source",
        "title_de",
    ]


def test_multiple_filter_args(patch_return_types):
    statistic1 = Field(
        name="BETR09",
        args={"FRUNW2": ["FRUART0111", "FRUART0112"]},
        fields=["FRUNW2", "value", "year"],
        default_fields=False,
    )
    multiple_args_query = Query.region(
        region="02", fields=[statistic1], default_fields=False
    )

    graphql_query = multiple_args_query.get_graphql_query()
    assert graphql_query[0] == re.sub(
        "    ",
        "",
        """{
            region (id: "02"){
                BETR09 (FRUNW2: [FRUART0111, FRUART0112]){FRUNW2 value year }
                }
            }""".replace(
            "\n", ""
        ),
    )


def test_all_regions(all_regions_query):
    graphql_query = all_regions_query.get_graphql_query()[0]
    expected_query = re.sub(
        r"\n\s+",
        "",
        """query ($page : Int, $itemsPerPage : Int) {
            allRegions (page: $page, itemsPerPage: $itemsPerPage){
                regions (parent: "11"){
                    id name WAHL09 (year: 2017){
                        value year PART04 }
                }
                page itemsPerPage total }
        }""",
    )
    assert graphql_query == expected_query


def test_nuts(field):
    query = Query.all_regions(
        parent="11", nuts=3, fields=["id", "name", field], default_fields=False
    )
    graphql_query = query.get_graphql_query()[0]
    assert graphql_query == re.sub(
        r"\n\s+",
        "",
        """query ($page : Int, $itemsPerPage : Int) {
            allRegions (page: $page, itemsPerPage: $itemsPerPage){
                regions (parent: "11", nuts: 3){
                    id name WAHL09 (year: 2017){value year PART04 }
                }
                page itemsPerPage total }
        }""",
    )


def test_lau(field):
    query = Query.all_regions(
        parent="11", lau=3, fields=["id", "name", field], default_fields=False
    )
    graphql_query = query.get_graphql_query()[0]
    assert re.sub(" +", " ", graphql_query.replace("\n", " ")) == re.sub(
        r"\n\s+",
        "",
        """query ($page : Int, $itemsPerPage : Int) {
            allRegions (page: $page, itemsPerPage: $itemsPerPage){
                regions (parent: "11", lau: 3){
                    id name WAHL09 (year: 2017){value year PART04 }
                }
                page itemsPerPage total }
        }""",
    )


def test_filter_for_all(query):
    field = Field(
        name="WAHL09",
        args={"year": 2017, "PART04": "ALL"},
        fields=["value", "PART04"],
        default_fields=False,
        return_type="WAHL09",
    )
    query = Query.region(region="09", fields=["id", "name", field])
    graphql_query = query.get_graphql_query()
    assert graphql_query[0] == re.sub(
        "    ",
        "",
        """{
            region (id: "09"){
                id name WAHL09 (
                    year: 2017, filter:{ PART04: { nin: []}}){
                        value PART04 }
                }
        }""".replace(
            "\n", ""
        ),
    )


def test_add_fields_stepwise(patch_return_types):
    query = Query.region(region="11", default_fields=False)
    statistic1 = query.add_field("BEV001", default_fields=False)
    statistic1.add_field("year")
    statistic2 = Field(
        name="WAHL09",
        args={"year": 2017, "PART04": "ALL"},
        fields=["value", "PART04"],
        default_fields=False,
        return_type="WAHL09",
    )
    query.add_field(statistic2)

    query2 = Query.region(
        region="11",
        fields=[
            Field(
                name="BEV001",
                fields=["year"],
                default_fields=False,
                return_type="BEV001",
            ),
            Field(
                name="WAHL09",
                args={"year": 2017, "PART04": "ALL"},
                fields=["value", "PART04"],
                default_fields=False,
                return_type="WAHL09",
            ),
        ],
        default_fields=False,
    )
    assert query.get_graphql_query() == query2.get_graphql_query()

    graphql_query = query.get_graphql_query()
    assert graphql_query[0] == re.sub(
        "    ",
        "",
        """{
                region (id: "11"){
                    BEV001 {year }
                    WAHL09 (year: 2017, filter:{ PART04: { nin: []}}){value PART04 }
                }
        }""".replace(
            "\n", ""
        ),
    )


def test_add_fields_all_regions(patch_return_types):
    all_reg_query = Query.all_regions(parent="11")
    all_reg_query.add_field("BEV001")

    graphql_query = all_reg_query.get_graphql_query()[0]
    assert graphql_query == re.sub(
        r"\n\s+",
        "",
        """query ($page : Int, $itemsPerPage : Int) {
            allRegions (page: $page, itemsPerPage: $itemsPerPage){
                regions (parent: "11"){
                    id name BEV001 {
                        year value source {title_de valid_from periodicity name url }}
                }
                page itemsPerPage total }
        }""",
    )


def test_add_args_stepwise(patch_return_types):
    query = Query.region(region="11")
    statistic1 = query.add_field("BEV001")
    statistic1.add_field("year")
    statistic1.add_args({"year": 2017})

    query2 = Query.region(
        region="11", fields=[Field(name="BEV001", args={"year": 2017}, fields=["year"])]
    )

    assert query.get_graphql_query() == query2.get_graphql_query()


def test_default_fields(query_default):
    graphql_query = query_default.get_graphql_query()
    assert graphql_query[0] == re.sub(
        "    ",
        "",
        """{region (id: "09"){id name BEV001
            {year value source
            {title_de valid_from periodicity name url }}}}""".replace(
            "\n", " "
        ),
    )


def test_drop_field(query):
    query = query.drop_field("BEV001")
    assert query.get_fields() == ["region"]


def test_drop_field_without_assignment(query):
    query.drop_field("BEV001")
    assert query.get_fields() == ["region"]


def test_drop_field_all_regions(all_regions_query):
    all_regions_query = all_regions_query.drop_field("WAHL09")
    assert all_regions_query.get_fields() == [
        "allRegions",
        "regions",
        "id",
        "name",
        "page",
        "itemsPerPage",
        "total",
    ]


def test_arguments_info_formatting(
    mocked_arguments, mocked_enum_placeholder, field_default
):
    info = field_default._arguments_info_formatter(mocked_arguments)
    expected_info = """\x1b[4myear\x1b[0m: LIST of type SCALAR(Int)

    \x1b[4mNAT\x1b[0m: LIST of type ENUM(NAT)
    enum values:
    MOCKED ENUM VALUES"""

    assert re.sub(r"\s+", "", info) == re.sub(r"\s+", "", expected_info)


def test_fields_info_formatting(meta_fields, field_default):
    info = field_default._fields_info_formatter(meta_fields)
    expected_info = """id: Interne eindeutige ID
    year: Jahr des Stichtages
    value: Wert
    source: Quellenverweis zur GENESIS Regionaldatenbank
    PART04: Parteien"""

    assert re.sub(r"\s+", "", info) == re.sub(r"\s+", "", expected_info)


def test_enum_info_formatting(enum_input, query):
    info = query.add_field("BEV001").add_field("NAT")._enum_info_formatter(enum_input)
    expected_info = """
    NATA: Ausländer(innen)
    NATD: Deutsche
    GESAMT: Gesamt"""

    assert re.sub(r"\s+", "", info) == re.sub(r"\s+", "", expected_info)


def test_invalid_region_name_raises_exception():
    q = Query.region("jodelverein")
    q.add_field("BEV001")
    with pytest.raises(ValueError, match=r"region is invalid."):
        q.results()


def test_missing_statistic_field_raises_exception():
    q = Query.region("09162000")
    with pytest.raises(Exception, match=r"add .* field"):
        q.results()
