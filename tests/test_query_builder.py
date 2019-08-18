import pytest
import re
from datenguide_python import Field, Query


@pytest.fixture
def field():
    return Field("WAHL09", args={"year": 2017}, fields=["value", "year", "PART04"])


@pytest.fixture
def query():
    return Query.regionQuery(region="09", fields=["BEV001"])


@pytest.fixture
def complex_query(field):
    return Query.regionQuery(region="09", fields=["id", "name", field])


@pytest.fixture
def more_complex_query(complex_query):
    query = complex_query
    source = Field("source", fields=["title_de"])
    statistic2 = Field(
        name="BEV001", args={"statistics": "R12612"}, fields=["value", "year", source]
    )
    query.add_field(statistic2)
    return query


@pytest.fixture
def no_args_query():
    field = Field(name="WAHL09", fields=["value"])
    return Query.regionQuery(region="09", fields=["id", "name", field])


@pytest.fixture
def multiple_args_query():
    statistic1 = Field(
        name="BETR09",
        args={"FRUNW2": ["FRUART0111", "FRUART0112"]},
        fields=["FRUNW2", "value", "year"],
    )
    return Query.regionQuery(region="02", fields=[statistic1])


@pytest.fixture
def all_regions_query(field):
    return Query.allRegionsQuery(parent="11", fields=["id", "name", field])


@pytest.fixture
def nuts_query(field):
    return Query.allRegionsQuery(parent="11", nuts=3, fields=["id", "name", field])


@pytest.fixture
def lau_query(field):
    return Query.allRegionsQuery(parent="11", lau=3, fields=["id", "name", field])


def test_create_query_is_class_query(query):
    assert isinstance(query, Query)


def test_create_query_class_without_start_filed_raises_error():
    with pytest.raises(TypeError):
        Query()


def test_basic_graphql_string(query):
    graphql_query = query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", " ")) == re.sub(
        " +", " ", """{region(id: "09"){BEV001 }}""".replace("\n", " ")
    )


def test_get_fields_to_query():
    field = Field(name="WAHL09", args={"year": 2017}, fields=["value", "PART04"])
    subfields_string = field._get_fields_to_query(field)
    assert subfields_string == "WAHL09(year: 2017){value PART04 }"


def test_get_complex_graphql_string(complex_query):
    graphql_query = complex_query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", " ")) == re.sub(
        "    ",
        "",
        """{
            region(id: "09"){
                id name WAHL09(year: 2017){value year PART04 }
                }
            }""".replace(
            "\n", ""
        ),
    )


def test_get_complex_graphql_string_without_args(no_args_query):
    graphql_query = no_args_query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", " ")) == re.sub(
        "    ",
        "",
        """{
        region(id: "09"){
            id name WAHL09{value }}
            }""".replace(
            "\n", ""
        ),
    )


def test_get_multiple_stats(more_complex_query):
    graphql_query = more_complex_query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", " ")) == re.sub(
        "    ",
        "",
        """{
        region(id: "09"){
            id name WAHL09(year: 2017){value year PART04 }
            BEV001(statistics: R12612){value year source{title_de }}}
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


def test_multiple_filter_args(multiple_args_query):
    graphql_query = multiple_args_query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", " ")) == re.sub(
        "    ",
        "",
        """{
            region(id: "02"){
                BETR09(FRUNW2: [FRUART0111, FRUART0112]){FRUNW2 value year }
                }
            }""".replace(
            "\n", ""
        ),
    )


def test_all_regions(all_regions_query):

    graphql_query = all_regions_query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", " ")) == re.sub(
        "    ",
        "",
        """{
            allRegions(page: $page, itemsPerPage: $itemsPerPage){
                regions(parent: "11"){
                    id name WAHL09(year: 2017){
                        value year PART04 }
                }
                page itemsPerPage total }
        }""".replace(
            "\n", ""
        ),
    )


def test_nuts(nuts_query):
    query = nuts_query
    graphql_query = query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", " ")) == re.sub(
        "    ",
        "",
        """{
            allRegions(page: $page, itemsPerPage: $itemsPerPage){
                regions(parent: "11", nuts: 3){
                    id name WAHL09(year: 2017){value year PART04 }
                }
                page itemsPerPage total }
        }""".replace(
            "\n", ""
        ),
    )


def test_lau(lau_query):
    query = lau_query
    graphql_query = query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", " ")) == re.sub(
        "    ",
        "",
        """{
            allRegions(page: $page, itemsPerPage: $itemsPerPage){
                regions(parent: "11", lau: 3){
                    id name WAHL09(year: 2017){value year PART04 }
                }
                page itemsPerPage total }
        }""".replace(
            "\n", ""
        ),
    )


def test_filter_for_all(query):
    field = Field(
        name="WAHL09", args={"year": 2017, "PART04": "ALL"}, fields=["value", "PART04"]
    )
    query = Query.regionQuery(region="09", fields=["id", "name", field])
    graphql_query = query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", " ")) == re.sub(
        "    ",
        "",
        """{
            region(id: "09"){
                id name WAHL09(
                    year: 2017, filter:{ PART04: { nin: []}}){
                        value PART04 }
                }
        }""".replace(
            "\n", ""
        ),
    )


def test_add_fields_stepwise():
    query = Query.regionQuery(region="11")
    statistic1 = query.add_field("BEV001")
    statistic1.add_field("year")
    statistic2 = Field(
        name="WAHL09", args={"year": 2017, "PART04": "ALL"}, fields=["value", "PART04"]
    )
    query.add_field(statistic2)

    assert query == Query.regionQuery(
        region="11",
        fields=[
            Field(name="BEV001", fields=[Field(name="year")]),
            Field(
                name="WAHL09",
                args={"year": 2017, "PART04": "ALL"},
                fields=["value", "PART04"],
            ),
        ],
    )

    graphql_query = query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", " ")) == re.sub(
        "    ",
        "",
        """{
                region(id: "11"){
                    BEV001{year}
                    WAHL09(year: 2017, filter:{ PART04: { nin: []}}){value PART04 }
                }
        }""".replace(
            "\n", ""
        ),
    )


def test_add_args_stepwise():
    query = Query.regionQuery(region="11")
    statistic1 = query.add_field("BEV001")
    statistic1.add_field("year")
    statistic1.add_args({"year": 2017})

    assert query == Query.regionQuery(
        region="11",
        fields=[Field(name="BEV001", args={"year": 2017}, fields=[Field(name="year")])],
    )
