import pytest
import re
from datenguide_python import Field, Query


@pytest.fixture
def field_default():
    return Field("WAHL09", args={"year": 2017}, fields=["PART04"], return_type="WAHL09")


@pytest.fixture
def query_default():
    return Query.regionQuery(region="09", fields=["BEV001"])


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
    return Query.regionQuery(region="09", fields=["BEV001"], default_fields=False)


@pytest.fixture
def complex_query(field):
    return Query.regionQuery(
        region="09", fields=["id", "name", field], default_fields=False
    )


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
    assert graphql_query == re.sub(
        " +", " ", """{region (id: "09"){BEV001 }}""".replace("\n", " ")
    )


def test_get_fields_to_query():
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
    assert graphql_query == re.sub(
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


def test_get_complex_graphql_string_without_args():
    field = Field(name="WAHL09", fields=["value"], default_fields=False)
    no_args_query = Query.regionQuery(
        region="09", fields=["id", "name", field], default_fields=False
    )

    graphql_query = no_args_query.get_graphql_query()
    assert graphql_query == re.sub(
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
    assert graphql_query == re.sub(
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


def test_multiple_filter_args():
    statistic1 = Field(
        name="BETR09",
        args={"FRUNW2": ["FRUART0111", "FRUART0112"]},
        fields=["FRUNW2", "value", "year"],
        default_fields=False,
    )
    multiple_args_query = Query.regionQuery(
        region="02", fields=[statistic1], default_fields=False
    )

    graphql_query = multiple_args_query.get_graphql_query()
    assert graphql_query == re.sub(
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


def test_all_regions(field):
    all_regions_query = Query.allRegionsQuery(
        parent="11", fields=["id", "name", field], default_fields=False
    )
    graphql_query = all_regions_query.get_graphql_query()
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
    query = Query.allRegionsQuery(
        parent="11", nuts=3, fields=["id", "name", field], default_fields=False
    )

    graphql_query = query.get_graphql_query()
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
    query = Query.allRegionsQuery(
        parent="11", lau=3, fields=["id", "name", field], default_fields=False
    )
    graphql_query = query.get_graphql_query()
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
    query = Query.regionQuery(region="09", fields=["id", "name", field])
    graphql_query = query.get_graphql_query()
    assert graphql_query == re.sub(
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


def test_add_fields_stepwise():
    query = Query.regionQuery(region="11", default_fields=False)
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

    query2 = Query.regionQuery(
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
    assert graphql_query == re.sub(
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


def test_add_fields_all_regions():
    all_reg_query = Query.allRegionsQuery(parent="11")
    all_reg_query.add_field("BEV001")

    graphql_query = all_reg_query.get_graphql_query()
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


def test_add_args_stepwise():
    query = Query.regionQuery(region="11")
    statistic1 = query.add_field("BEV001")
    statistic1.add_field("year")
    statistic1.add_args({"year": 2017})

    query2 = Query.regionQuery(
        region="11", fields=[Field(name="BEV001", args={"year": 2017}, fields=["year"])]
    )

    assert query.get_graphql_query() == query2.get_graphql_query()


def test_default_fields(query_default):
    graphql_query = query_default.get_graphql_query()
    assert graphql_query == re.sub(
        "    ",
        "",
        """{region (id: "09"){id name BEV001
            {year value source
            {title_de valid_from periodicity name url }}}}""".replace(
            "\n", " "
        ),
    )


def test_get_all_stats_info():
    info = Query.get_info()
    assert "name" in info.fields


def test_get_field_info():
    info = Query.get_info("BEV001")
    assert "BEVM01" in info.fields
