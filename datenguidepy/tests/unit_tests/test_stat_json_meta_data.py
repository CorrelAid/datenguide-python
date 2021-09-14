from datenguidepy.query_execution import StatisticsSchemaJsonMetaDataProvider


def test_get_query_specific_stat_meta():
    field_type_list = [
        ("id", "String"),
        ("name", "String"),
        ("WAHL09", "WAHL09"),
        ("PART04", "PART04"),
        ("year", "Int"),
        ("value", "Float"),
    ]
    query_stat_meta = StatisticsSchemaJsonMetaDataProvider().get_query_stat_meta(
        field_type_list
    )
    expected_stat_meta = {"WAHL09": "Gültige Zweitstimmen"}
    assert query_stat_meta == expected_stat_meta


def test_get_query_specific_enum_meta():
    field_type_list = [
        ("id", "String"),
        ("name", "String"),
        ("WAHL09", "WAHL09"),
        ("PART04", "PART04"),
        ("year", "Int"),
        ("value", "Float"),
    ]
    query_stat_meta = StatisticsSchemaJsonMetaDataProvider().get_query_enum_meta(
        field_type_list
    )
    expected_stat_meta = {
        "PART04": dict(
            [
                ("AFD", "AfD"),
                ("B90_GRUENE", "GRÜNE"),
                ("CDU", "CDU/CSU"),
                ("DIELINKE", "DIE LINKE"),
                ("FDP", "FDP"),
                ("SONSTIGE", "Sonstige Parteien"),
                ("SPD", "SPD"),
                ("GESAMT", "Gesamt"),
            ]
        )
    }
    assert query_stat_meta == expected_stat_meta


def test_get_query_specific_unit_meta():

    field_type_list = [
        ("id", "String"),
        ("name", "String"),
        ("WAHL09", "WAHL09"),
        ("PART04", "PART04"),
        ("year", "Int"),
        ("value", "Float"),
    ]
    query_stat_meta = StatisticsSchemaJsonMetaDataProvider().get_query_unit_meta(
        field_type_list
    )

    expected_stat_meta = {"WAHL09": "Anzahl"}
    assert query_stat_meta == expected_stat_meta
