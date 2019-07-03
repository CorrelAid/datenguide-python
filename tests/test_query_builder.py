
import pytest

import datenguide_python
from datenguide_python import query_builder


@pytest.fixture
def args():
    """Sample pytest fixture.
    See more at: http://doc.pytest.org/en/latest/fixture.html
    """

    # set arguments
    pass


def test_create_query_class_with_args_instance():
    query = query_builder.Query(region='09', field1='BEV001')
    assert isinstance(query, query_builder.Query)


def test_create_query_class_without_args_throws_error():
    with pytest.raises(TypeError):
        query_builder.Query()


def test_basic_graphql_string():
    query = query_builder.Query(region='09', field1='BEV001')
    print(query.get_graphql_query())
    graphql_query = query.get_graphql_query()
    assert graphql_query == """
                {
                    region(id:"09") {
                        BEV001
                    }
                }
                """     