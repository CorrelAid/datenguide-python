
import pytest

import datenguide_python as dg
# from datenguide_python import query_builder


@pytest.fixture
def query():
    return dg.QueryBuilder(region='09', fields=['BEV001'])

@pytest.fixture
def complex_query():
        source = dg.ComplexField(
            field='source',
            subfields=['title_de']
        )

        statistic1 = dg.ComplexField(
            field='WAHL09',
            args={'year': 2017},
            subfields=['value', 'PART04', source])

        statistic2 = dg.ComplexField(
            field='BEV001',
            args={'statistics': 'R12612'},
            subfields=['value', 'year'])

        return dg.QueryBuilder(
            region='09',
            fields=['id', 'name', statistic1, statistic2])


def test_create_query_class_with_field_instance(query):
    assert isinstance(query, dg.QueryBuilder)


def test_create_query_class_without_field_throws_error():
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
    field = dg.ComplexField(
            field='WAHL09',
            args={'year': 2017},
            subfields=['value', 'PART04'])
    query = dg.QueryBuilder(region='09', fields=[field])
    subfields_string = query._get_fields_to_query()
    assert subfields_string == "WAHL09(year: 2017){value PART04 } "


def test_get_complex_graphql_string():
        field = dg.ComplexField(
            field='WAHL09',
            args={'year': 2017},
            subfields=['value', 'PART04'])
        query = dg.QueryBuilder(region='09', fields=['id', 'name', field])
        graphql_query = query.get_graphql_query()
        assert graphql_query == """
                {
                    region(id: "09") {
                        id name WAHL09(year: 2017){value PART04 } 
                    }
                }
                """


def test_get_complex_graphql_string_without_filter():
        field = dg.ComplexField(
            field='WAHL09',
            subfields=['value'])
        query = dg.QueryBuilder(region='09', fields=['id', 'name', field])
        graphql_query = query.get_graphql_query()
        assert graphql_query == """
                {
                    region(id: "09") {
                        id name WAHL09{value } 
                    }
                }
                """


def test_get_multiple_stats(complex_query):

        graphql_query = complex_query.get_graphql_query()
        assert graphql_query == """
                {
                    region(id: "09") {
                        id name WAHL09(year: 2017){value PART04 source{title_de } } BEV001(statistics: R12612){value year } 
                    }
                }
                """


def test_get_subfields(query):
    assert query.get_fields() == ['BEV001']


def test_get_subfields_complex():
    statistic1 = dg.ComplexField(
            field='WAHL09',
            args={'year': 2017},
            subfields=['value', 'PART04'])

    statistic2 = dg.ComplexField(
            field='BEV001',
            args={'statistics': 'R12612'},
            subfields=['value', 'year'])

    query = dg.QueryBuilder(
            region='09',
            fields=['id', 'name', statistic1, statistic2])
    assert query.get_fields() == ['id', 'name', statistic1, statistic2]