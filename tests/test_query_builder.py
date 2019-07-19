import pytest
import re
import datenguide_python as dg

# from datenguide_python import query_builder


@pytest.fixture
def query():
    return dg.QueryBuilder(region="09", fields=["BEV001"])


@pytest.fixture
def complex_query():
    source = dg.Field(name="source", subfields=["title_de"])

    statistic1 = dg.Field(
        name="WAHL09", args={"year": 2017}, subfields=["value", "PART04", source]
    )

    statistic2 = dg.Field(
        name="BEV001", args={"statistics": "R12612"}, subfields=["value", "year"]
    )

    return dg.QueryBuilder(region="09", fields=["id", "name", statistic1, statistic2])


def test_create_query_class_with_field_instance(query):
    assert isinstance(query, dg.QueryBuilder)


def test_create_query_class_without_field_throws_error():
    with pytest.raises(TypeError):
        dg.QueryBuilder()


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
    field = dg.Field(name="WAHL09", args={"year": 2017}, subfields=["value", "PART04"])
    query = dg.QueryBuilder(region="09", fields=[field])
    subfields_string = query._get_fields_to_query()
    assert subfields_string == "WAHL09(year: 2017){value PART04 }"


def test_get_complex_graphql_string():
    field = dg.Field(name="WAHL09", args={"year": 2017}, subfields=["value", "PART04"])
    query = dg.QueryBuilder(region="09", fields=["id", "name", field])
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
    field = dg.Field(name="WAHL09", subfields=["value"])
    query = dg.QueryBuilder(region="09", fields=["id", "name", field])
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


def test_get_subfields_complex():
    statistic1 = dg.Field(
        name="WAHL09", args={"year": 2017}, subfields=["value", "PART04"]
    )

    statistic2 = dg.Field(
        name="BEV001", args={"statistics": "R12612"}, subfields=["value", "year"]
    )

    query = dg.QueryBuilder(region="09", fields=["id", "name", statistic1, statistic2])
    assert query.get_fields() == ["id", "name", statistic1, statistic2]


def test_multiple_filter_args():
    statistic1 = dg.Field(
        name="BETR09",
        args={"FRUNW2": ["FRUART0111", "FRUART0112"]},
        subfields=["FRUNW2", "value", "year"],
    )

    query = dg.QueryBuilder(region="02", fields=[statistic1])
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
        subfields=["value", "year", "PART04"],
    )

    query = dg.QueryBuilder(parent="11", fields=["id", "name", statistic1])
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
