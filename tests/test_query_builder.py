import pytest
import re
import datenguide_python as dg


@pytest.fixture
def query():
    return dg.Query(region="09", fields=["BEV001"])


@pytest.fixture
def complex_query():
    source = dg.Field("source", fields=["title_de"])

    statistic1 = dg.Field(
        "WAHL09", args={"year": 2017}, fields=["value", "PART04", source]
    )

    statistic2 = dg.Field(
        name="BEV001", args={"statistics": "R12612"}, fields=["value", "year"]
    )

    return dg.Query(region="09", fields=["id", "name", statistic1, statistic2])


def test_create_query_class_with_field_instance(query):
    assert isinstance(query, dg.Query)


def test_create_query_class_without_field_throws_error():
    with pytest.raises(TypeError):
        dg.Query()


def test_basic_graphql_string(query):
    graphql_query = query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", " ")) == re.sub(
        " +",
        " ",
        """
                {
                    region(id: "09") {
                    BEV001
                    }
                }
                    """.replace(
            "\n", " "
        ),
    )


def test_get_fields_to_query():
    field = dg.Field(name="WAHL09", args={"year": 2017}, fields=["value", "PART04"])
    query = dg.Query(region="09", fields=[field])
    subfields_string = query._get_fields_to_query()
    assert subfields_string == "WAHL09(year: 2017){value PART04 }"


def test_get_complex_graphql_string():
    field = dg.Field(name="WAHL09", args={"year": 2017}, fields=["value", "PART04"])
    query = dg.Query(region="09", fields=["id", "name", field])
    graphql_query = query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", " ")) == re.sub(
        " +",
        " ",
        """
                {
                    region(id: "09") {
                    id name WAHL09(year: 2017){value PART04 }
                    }
                }
                    """.replace(
            "\n", " "
        ),
    )


def test_get_complex_graphql_string_without_filter():
    field = dg.Field(name="WAHL09", fields=["value"])
    query = dg.Query(region="09", fields=["id", "name", field])
    graphql_query = query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", " ")) == re.sub(
        " +",
        " ",
        """
            {
                region(id: "09") {
                    id name WAHL09{value }
                    }
                }
            """.replace(
            "\n", " "
        ),
    )


def test_get_multiple_stats(complex_query):

    graphql_query = complex_query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", " ")) == re.sub(
        " +",
        " ",
        """
            {
                region(id: "09") {
                    id name WAHL09(year: 2017){value PART04 source{title_de } }
                         BEV001(statistics: R12612){value year }
                }
            }
            """.replace(
            "\n", " "
        ),
    )


def test_get_subfields(query):
    assert query.get_fields() == ["BEV001"]


def test_get_subfields_complex(complex_query):
    assert complex_query.get_fields() == [
        "id",
        "name",
        "WAHL09",
        "value",
        "PART04",
        "source",
        "title_de",
        "BEV001",
        "value",
        "year",
    ]


def test_multiple_filter_args():
    statistic1 = dg.Field(
        name="BETR09",
        args={"FRUNW2": ["FRUART0111", "FRUART0112"]},
        fields=["FRUNW2", "value", "year"],
    )

    query = dg.Query(region="02", fields=[statistic1])
    graphql_query = query.get_graphql_query()

    assert re.sub(" +", " ", graphql_query.replace("\n", " ")) == re.sub(
        " +",
        " ",
        """
            {
                region(id: "02") {
                BETR09(FRUNW2: [FRUART0111, FRUART0112]){FRUNW2 value year }
                }
            }
                """.replace(
            "\n", " "
        ),
    )


def test_filter_for_all_subtypes():
    assert True


def test_all_regions():
    statistic1 = dg.Field(
        name="WAHL09",
        args={"year": 2017, "PART04": "B90_GRUENE"},
        fields=["value", "year", "PART04"],
    )

    query = dg.Query(parent="11", fields=["id", "name", statistic1])
    graphql_query = query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", "")) == re.sub(
        " +",
        " ",
        """
                {
                    allRegions(page: $page, itemsPerPage:$itemsPerPage) {
                        regions(parent: "11") {
                            id name WAHL09(year: 2017, PART04:
                            B90_GRUENE){value year PART04 }
                        }
                        page
                        itemsPerPage
                        total
                    }
                }
                """.replace(
            "\n", ""
        ),
    )


def test_nuts():
    statistic1 = dg.Field(
        name="WAHL09",
        args={"year": 2017, "PART04": "B90_GRUENE"},
        fields=["value", "year", "PART04"],
    )

    query = dg.Query(parent="11", nuts=3, fields=["id", "name", statistic1])
    graphql_query = query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", "")) == re.sub(
        " +",
        " ",
        """
                {
                    allRegions(page: $page, itemsPerPage:$itemsPerPage) {
                        regions(parent: "11", nuts: 3) {
                            id name WAHL09(year: 2017, PART04:
                            B90_GRUENE){value year PART04 }
                        }
                        page
                        itemsPerPage
                        total
                    }
                }
                """.replace(
            "\n", ""
        ),
    )


def test_lau():
    statistic1 = dg.Field(
        name="WAHL09",
        args={"year": 2017, "PART04": "B90_GRUENE"},
        fields=["value", "year", "PART04"],
    )

    query = dg.Query(parent="11", lau=3, fields=["id", "name", statistic1])
    graphql_query = query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", "")) == re.sub(
        " +",
        " ",
        """
                {
                    allRegions(page: $page, itemsPerPage:$itemsPerPage) {
                        regions(parent: "11", lau: 3) {
                            id name WAHL09(year: 2017, PART04:
                            B90_GRUENE){value year PART04 }
                        }
                        page
                        itemsPerPage
                        total
                    }
                }
                """.replace(
            "\n", ""
        ),
    )


def test_filter_for_all(query):
    field = dg.Field(
        name="WAHL09", args={"year": 2017, "PART04": "ALL"}, fields=["value", "PART04"]
    )
    query = dg.Query(region="09", fields=["id", "name", field])
    graphql_query = query.get_graphql_query()
    assert re.sub(" +", " ", graphql_query.replace("\n", "")) == re.sub(
        " +",
        " ",
        """
            { region(id: "09") {
                id
                name
                WAHL09(year: 2017, filter:{ PART04: { nin: []}}){value PART04 }
                }
            }
                    """.replace(
            "\n", ""
        ),
    )


def test_add_fields_stepwise():

    query = dg.Query(region="11")
    statistic1 = query.add_field("BEV001")
    statistic1.add_field("year")
    statistic2 = dg.Field(
        name="WAHL09", args={"year": 2017, "PART04": "ALL"}, fields=["value", "PART04"]
    )
    query.add_field(statistic2)

    assert query == dg.Query(
        region="11",
        fields=[
            dg.Field(name="BEV001", fields=[dg.Field(name="year")]),
            dg.Field(
                name="WAHL09",
                args={"year": 2017, "PART04": "ALL"},
                fields=["value", "PART04"],
            ),
        ],
    )

    query_string = query.get_graphql_query()
    assert re.sub(" +", " ", query_string.replace("\n", " ")) == re.sub(
        " +",
        " ",
        """
            {
                region(id: "11") {
                    BEV001{year}
                    WAHL09(year: 2017, filter:{ PART04: { nin: []}}){value PART04 }
                }
            }
            """.replace(
            "\n", " "
        ),
    )


def test_add_args_stepwise():
    query = dg.Query(region="11")
    statistic1 = query.add_field("BEV001")
    statistic1.add_field("year")
    statistic1.add_args({"year": 2017})

    assert query == dg.Query(
        region="11",
        fields=[
            dg.Field(name="BEV001", args={"year": 2017}, fields=[dg.Field(name="year")])
        ],
    )
