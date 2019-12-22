import pytest
import re
import sys
import io
import pandas as pd
from datenguidepy import Field, Query


@pytest.fixture
def field_default():
    return Field("WAHL09", args={"year": 2017}, fields=["PART04"], return_type="WAHL09")


@pytest.fixture
def query_default():
    return Query.region(region="09", fields=["BEV001"])


@pytest.fixture
def query_with_enum():
    q = Query.region("09", default_fields=False)
    stat = q.add_field("WAHL09")
    stat.add_field("PART04")
    stat.add_field("year")
    stat.add_field("value")
    return q


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
    return Query.region(region="09", fields=["BEV001"], default_fields=False)


@pytest.fixture
def all_regions_query(field):
    return Query.all_regions(
        parent="11", fields=["id", "name", field], default_fields=False
    )


@pytest.fixture
def complex_query(field):
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


def test_get_all_stats_info():
    info = Query.all_regions().get_info()
    assert "name" in info.fields


def test_get_field_info():
    info = Query.all_regions().get_info("BEV001")
    assert "BEVM01" in info.fields


def test_process_query(query_default):
    df = query_default.results()
    assert isinstance(df, pd.DataFrame)


# dependent on api details
@pytest.mark.xfail
def test_arguments_info(query_default):
    stat = query_default.add_field("BEV001")
    info = stat.arguments_info()
    expected_info = """\x1b[4myear\x1b[0m: LIST of type SCALAR(Int)

\x1b[4mstatistics\x1b[0m: LIST of type ENUM(BEV001Statistics)
enum values:
R12612: Statistik der Geburten

\x1b[4mALTMT1\x1b[0m: LIST of type ENUM(ALTMT1)
enum values:
ALT000B20: unter 20 Jahre
ALT020B25: 20 bis unter 25 Jahre
ALT025B30: 25 bis unter 30 Jahre
ALT030B35: 30 bis unter 35 Jahre
ALT035B40: 35 bis unter 40 Jahre
ALT040UM: 40 Jahre und mehr
GESAMT: Gesamt

\x1b[4mBEVM01\x1b[0m: LIST of type ENUM(BEVM01)
enum values:
MONAT01: Januar
MONAT02: Februar
MONAT03: März
MONAT04: April
MONAT05: Mai
MONAT06: Juni
MONAT07: Juli
MONAT08: August
MONAT09: September
MONAT10: Oktober
MONAT11: November
MONAT12: Dezember
GESAMT: Gesamt

\x1b[4mGES\x1b[0m: LIST of type ENUM(GES)
enum values:
GESM: männlich
GESW: weiblich
GESAMT: Gesamt

\x1b[4mLEGIT2\x1b[0m: LIST of type ENUM(LEGIT2)
enum values:
LEGIT01A: Eltern miteinander verheiratet
LEGIT02A: Eltern nicht miteinander verheiratet
GESAMT: Gesamt

\x1b[4mNAT\x1b[0m: LIST of type ENUM(NAT)
enum values:
NATA: Ausländer(innen)
NATD: Deutsche
GESAMT: Gesamt

\x1b[4mfilter\x1b[0m: INPUT_OBJECT(BEV001Filter)"""
    assert info == expected_info


@pytest.mark.xfail
def test_field_info(query_default):
    stat = query_default.add_field("BEV001")
    info = stat.fields_info()
    assert (
        info
        == """id: Interne eindeutige ID
year: Jahr des Stichtages
value: Wert
source: Quellenverweis zur GENESIS Regionaldatenbank
ALTMT1: Altersgruppen der Mutter (unter 20 bis 40 u.m.)
BEVM01: Monat der Geburt
GES: Geschlecht
LEGIT2: Legitimität
NAT: Nationalität"""
    )


# possibly a unittest as it it uses statistics json by default
def test_enum_info(query_default):
    stat = query_default.add_field("BEV001")
    ges = stat.add_field("GES")
    info = ges.enum_info()
    expected_info = """GESM: männlich
GESW: weiblich
GESAMT: Gesamt"""
    assert info == expected_info


def test_description(query_default):
    stat = query_default.add_field("BEV001")
    descr = stat.description()
    # assert descr == "Lebend Geborene"
    assert (
        descr == '**BEV001**\n*aus GENESIS-Statistik "Statistik der Geburten" 12612)*'
    )


@pytest.mark.xfail
def test_get_info_stat(query_default):
    stringio = io.StringIO()
    sys.stdout = stringio
    stat = query_default.add_field("BEV001")
    stat.get_info()
    info = re.sub(r"\n", "", stringio.getvalue())
    print(info)
    expected_info = re.sub(
        r"\n\s+",
        "",
        """\x1b[1mkind:\x1b[0m
        OBJECT

        \x1b[1mdescription:\x1b[0m
        BEV001

        \x1b[1marguments:\x1b[0m
        \x1b[4myear\x1b[0m: LIST of type SCALAR(Int)

        \x1b[4mstatistics\x1b[0m: LIST of type ENUM(BEV001Statistics)
        enum values:
        R12612: Statistik der Geburten

        \x1b[4mALTMT1\x1b[0m: LIST of type ENUM(ALTMT1)
        enum values:
        ALT000B20: unter 20 Jahre
        ALT020B25: 20 bis unter 25 Jahre
        ALT025B30: 25 bis unter 30 Jahre
        ALT030B35: 30 bis unter 35 Jahre
        ALT035B40: 35 bis unter 40 Jahre
        ALT040UM: 40 Jahre und mehr
        GESAMT: Gesamt

        \x1b[4mBEVM01\x1b[0m: LIST of type ENUM(BEVM01)
        enum values:
        MONAT01: Januar
        MONAT02: Februar
        MONAT03: März
        MONAT04: April
        MONAT05: Mai
        MONAT06: Juni
        MONAT07: Juli
        MONAT08: August
        MONAT09: September
        MONAT10: Oktober
        MONAT11: November
        MONAT12: Dezember
        GESAMT: Gesamt

        \x1b[4mGES\x1b[0m: LIST of type ENUM(GES)
        enum values:
        GESM: männlich
        GESW: weiblich
        GESAMT: Gesamt

        \x1b[4mLEGIT2\x1b[0m: LIST of type ENUM(LEGIT2)
        enum values:
        LEGIT01A: Eltern miteinander verheiratet
        LEGIT02A: Eltern nicht miteinander verheiratet
        GESAMT: Gesamt

        \x1b[4mNAT\x1b[0m: LIST of type ENUM(NAT)
        enum values:
        NATA: Ausländer(innen)
        NATD: Deutsche
        GESAMT: Gesamt

        \x1b[4mfilter\x1b[0m: INPUT_OBJECT(BEV001Filter)

        \x1b[1mfields:\x1b[0m
        id: Interne eindeutige ID
        year: Jahr des Stichtages
        value: Wert
        source: Quellenverweis zur GENESIS Regionaldatenbank
        ALTMT1: Altersgruppen der Mutter (unter 20 bis 40 u.m.)
        BEVM01: Monat der Geburt
        GES: Geschlecht
        LEGIT2: Legitimität
        NAT: Nationalität

        \x1b[1menum values:\x1b[0m
        None""",
    )
    assert info == expected_info


def test_get_fields_with_return_type(field, query_with_enum):
    fields_and_types = field._get_fields_with_types()
    expected_fields_and_types = set(
        [
            ("WAHL09", "WAHL09"),
            ("value", "Float"),
            ("year", "Int"),
            ("PART04", "PART04"),
        ]
    )
    assert set(fields_and_types) == expected_fields_and_types

    fields_and_types = query_with_enum._get_fields_with_types()
    expected_fields_and_types = set(
        [
            ("WAHL09", "WAHL09"),
            ("region", "Region"),
            ("value", "Float"),
            ("year", "Int"),
            ("PART04", "PART04"),
        ]
    )
    assert set(fields_and_types) == expected_fields_and_types
