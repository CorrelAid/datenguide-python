import pandas as pd
import pytest
import os

from datenguidepy.output_transformer import QueryOutputTransformer
from tests.case_construction import construct_execution_results


@pytest.fixture
def query_result():
    abs_path = os.path.abspath(os.path.dirname(__file__))
    example_path = "examples/transformer_example1.json"
    full_path = os.path.join(abs_path, example_path)
    return construct_execution_results(full_path)


@pytest.fixture
def query_results_with_enum():
    abs_path = os.path.abspath(os.path.dirname(__file__))
    example_path = "examples/transformer_example2.json"
    full_path = os.path.join(abs_path, example_path)
    return construct_execution_results(full_path)


@pytest.fixture
def query_results_with_mult_enum():
    abs_path = os.path.abspath(os.path.dirname(__file__))
    example_path = "examples/multiple_enums.json"
    full_path = os.path.join(abs_path, example_path)
    return construct_execution_results(full_path)


def get_abs_path(fname):
    abs_path = os.path.abspath(os.path.dirname(__file__))
    full_path = os.path.join(abs_path, fname)
    return os.path.normpath(full_path)


@pytest.fixture
def query_result_with_autojoin_and_one_enum():
    full_path = get_abs_path("examples/auto_join_one_sided_enum.json")
    return construct_execution_results(full_path)


@pytest.fixture
def query_results_one_statistic_with_units():
    full_path = get_abs_path("examples/one_statistic_with_units.json")
    return construct_execution_results(full_path)


@pytest.fixture
def query_duplicates_for_states_single_stat():
    full_path = get_abs_path("examples/duplicates_for_states_single_stat.json")
    return construct_execution_results(full_path)


@pytest.fixture
def query_duplicates_for_states_multi_stat():
    full_path = get_abs_path("examples/duplicates_for_states_multi_stat.json")
    return construct_execution_results(full_path)


def test_output_transformer_with_one_statistic_and_units(
    query_results_one_statistic_with_units
):
    """check if units were added correctly"""
    qOutTrans = QueryOutputTransformer(query_results_one_statistic_with_units)
    data_transformed = qOutTrans.transform(add_units=True)

    assert data_transformed.loc[0, "TIE003_unit"] == "Anzahl"
    assert data_transformed.columns[5] == "TIE003_unit"


@pytest.fixture
def query_results_multiple_statistics_with_units():
    full_path = get_abs_path("examples/multiple_statistics_with_units.json")
    return construct_execution_results(full_path)


def test_output_transformer_with_multiple_statistics_and_units(
    query_results_multiple_statistics_with_units
):
    """check if units were added correctly"""
    qOutTrans = QueryOutputTransformer(query_results_multiple_statistics_with_units)
    data_transformed = qOutTrans.transform(add_units=True)

    assert data_transformed.iloc[1, range(4, 15, 2)].to_list() == [
        "Prozent",
        "Prozent",
        "Prozent",
        "Prozent",
        "Prozent",
        "kg",
    ]
    assert data_transformed.columns[range(4, 15, 2)].to_list() == [
        "AI0203_unit",
        "AI0204_unit",
        "AI0205_unit",
        "AI0206_unit",
        "AI0207_unit",
        "AI1902_unit",
    ]


def test_output_transformer_defaults(query_result):
    """ start test of output transformer """
    qOutTrans = QueryOutputTransformer(query_result)

    data_transformed = qOutTrans.transform()

    # test whether transformed output data is a dataframe
    assert type(data_transformed) == pd.DataFrame, "transformed data is not a dataframe"

    assert "id" in data_transformed.columns, "no id colum"
    assert "name" in data_transformed.columns, "no name colum"
    assert "year" in data_transformed.columns, "no year colum"
    assert "BEVMK3" in data_transformed.columns, "statistic values are missing"
    assert (
        "BEVMK3_value" not in data_transformed.columns
    ), "old statistics name still present"

    # columns of outdata should not contain json format
    lenlist = len(data_transformed.columns)
    checklist = ["." in data_transformed.columns[x] for x in range(lenlist)]
    assert not any(checklist), "hierarchy not properly transformed"


def test_output_transformer_format_options(query_result, query_results_with_enum):

    qOutTrans = QueryOutputTransformer(query_result)
    data_transformed = qOutTrans.transform(verbose_statistic_names=True)
    assert (
        # "Von der Scheidung betroffene Kinder (BEVMK3)" in data_transformed.columns
        "BEVMK3 (BEVMK3)"
        in data_transformed.columns
    ), "statistic values are missing"

    enum_values = {
        "AFD",
        "B90_GRUENE",
        "CDU",
        "DIELINKE",
        "FDP",
        "SONSTIGE",
        "SPD",
        "GESAMT",
        None,
    }
    enum_descriptions = {
        "AfD",
        "GRÜNE",
        "CDU/CSU",
        "DIE LINKE",
        "FDP",
        "Sonstige Parteien",
        "SPD",
        "Gesamt",
    }

    qOutTrans = QueryOutputTransformer(query_results_with_enum)
    data_transformed = qOutTrans.transform()
    assert set(data_transformed["PART04"]).issubset(enum_values)

    qOutTrans = QueryOutputTransformer(query_results_with_enum)
    data_transformed = qOutTrans.transform(verbose_enum_values=True)
    assert set(data_transformed["PART04"]).issubset(enum_descriptions)

    qOutTrans = QueryOutputTransformer(query_results_with_enum)
    data_transformed = qOutTrans.transform(
        verbose_enum_values=True, verbose_statistic_names=True
    )
    # assert "Gültige Zweitstimmen (WAHL09)" in data_transformed
    assert "WAHL09 (WAHL09)" in data_transformed


def test_output_transformer_format_options_multi_enum(query_results_with_mult_enum):
    qOutTrans = QueryOutputTransformer(query_results_with_mult_enum)
    data_transformed = qOutTrans.transform(verbose_enum_values=False)
    assert data_transformed["ADVNW2"].iloc[0] == "ADVTN420"
    assert data_transformed["ADVNW1"].iloc[0] is None

    data_transformed = qOutTrans.transform(verbose_enum_values=True)
    print(data_transformed.head())
    assert data_transformed["ADVNW2"].iloc[0] == "Grünanlage"
    assert data_transformed["ADVNW1"].iloc[0] == "Gesamt"


def test_output_transformer_auto_join_enum(query_result_with_autojoin_and_one_enum):
    qOutTrans = QueryOutputTransformer(query_result_with_autojoin_and_one_enum)
    data_transformed = qOutTrans.transform(verbose_enum_values=False)
    assert "BEVSTD_GES" in data_transformed
    assert data_transformed.columns.get_loc("BEVSTD_GES") <= 8
    assert list(data_transformed.BEVSTD_GES.unique()) == [None]

    data_transformed = qOutTrans.transform(verbose_enum_values=True)
    assert "BEVSTD_GES" in data_transformed
    assert list(data_transformed.BEVSTD_GES.unique()) == ["Gesamt"]


def test_dumplicate_removal_single(query_duplicates_for_states_single_stat):
    qOutTrans = QueryOutputTransformer(query_duplicates_for_states_single_stat)
    data_transformed = qOutTrans.transform(remove_duplicates=False)
    assert all(data_transformed.name.value_counts() == 2)

    data_transformed = qOutTrans.transform(remove_duplicates=True)
    assert all(data_transformed.name.value_counts() == 1)


def test_dumplicate_removal_multi(query_duplicates_for_states_multi_stat):
    qOutTrans = QueryOutputTransformer(query_duplicates_for_states_multi_stat)
    data_transformed = qOutTrans.transform(remove_duplicates=False)
    assert all(data_transformed.name.value_counts() == 4)

    data_transformed = qOutTrans.transform(remove_duplicates=True)
    assert all(data_transformed.name.value_counts() == 1)
