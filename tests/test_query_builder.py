
import pytest

import datenguide_python as dg
# from datenguide_python import query_builder


@pytest.fixture
def query():
    return dg.QueryBuilder(region='09', fields=['BEV001'])

@pytest.fixture
def complex_query():
        statistic1 = dg.ComplexField(
            statistic='WAHL09',
            filters={'year': 2017},
            fields=['value', 'PART04'])

        statistic2 = dg.ComplexField(
            statistic='BEV001',
            filters={'statistics': 'R12612'},
            fields=['value', 'year'])

        return dg.QueryBuilder(
            region='09',
            fields=['id', 'name', statistic1, statistic2])


def test_create_query_class_with_args_instance(query):
    assert isinstance(query, dg.QueryBuilder)


def test_create_query_class_without_args_throws_error():
    with pytest.raises(TypeError):
        dg.QueryBuilder()


def test_basic_graphql_string(query):
    graphql_query = query.get_graphql_query()
    assert graphql_query == """
                {
                    region(id: "09") {
                        BEV001 
                    }
                }
                """   


def test_get_fields_to_query():
    statistic = dg.ComplexField(
            statistic='WAHL09',
            filters={'year': 2017},
            fields=['value', 'PART04'])
    query = dg.QueryBuilder(region='09', fields=[statistic])
    fields_string = query._get_fields_to_query()
    assert fields_string == "WAHL09(year: 2017){value PART04} "


def test_get_complex_graphql_string():
        statistic = dg.ComplexField(
            statistic='WAHL09',
            filters={'year': 2017},
            fields=['value', 'PART04'])
        query = dg.QueryBuilder(region='09', fields=['id', 'name', statistic])
        graphql_query = query.get_graphql_query()
        assert graphql_query == """
                {
                    region(id: "09") {
                        id name WAHL09(year: 2017){value PART04} 
                    }
                }
                """


def test_get_multiple_stats(complex_query):

        graphql_query = complex_query.get_graphql_query()
        assert graphql_query == """
                {
                    region(id: "09") {
                        id name WAHL09(year: 2017){value PART04} BEV001(statistics: R12612){value year} 
                    }
                }
                """


def test_get_fields(query):
    assert query.get_fields() == ['BEV001']


def test_get_fields_complex():
    statistic1 = dg.ComplexField(
            statistic='WAHL09',
            filters={'year': 2017},
            fields=['value', 'PART04'])

    statistic2 = dg.ComplexField(
            statistic='BEV001',
            filters={'statistics': 'R12612'},
            fields=['value', 'year'])

    query = dg.QueryBuilder(
            region='09',
            fields=['id', 'name', statistic1, statistic2])
    assert query.get_fields() == ['id', 'name', statistic1, statistic2]