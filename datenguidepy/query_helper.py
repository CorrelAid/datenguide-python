from datenguidepy.query_builder import Query
from datenguidepy.query_execution import (
    QueryExecutioner,
    ExecutionResults,
    DEFAULT_STATISTICS_META_DATA_PROVIDER,
)
from datenguidepy.translation import DEFAULT_TRANSLATION_PROVIDER, TranslationProvider

from typing import Dict, Any, cast, Optional, List
import pandas as pd
from functools import partial

import os

PACKAGE_DATA_DIR = "package_data"
PACKAGE_DATA_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), PACKAGE_DATA_DIR
)
ALL_REGIONS: pd.DataFrame = pd.read_csv(
    os.path.join(PACKAGE_DATA_PATH, "regions.csv"), index_col="region_id"
)


class ConfigMapping:
    """[summary]

    :param mapping: [description]
    :type mapping: Dict[str, Any]
    """

    def __init__(self, mapping: Dict[str, Any]):

        self._mapping = mapping

    def __getattr__(self, k: str) -> Any:
        return self._mapping[k]

    def __dir__(self):
        return list(self._mapping.keys())

    def __repr__(self):
        return "\n".join(
            name.ljust(30, ".") + " " + id for name, id in self._mapping.items()
        )

    def __iter__(self):
        return self._mapping.values().__iter__()


def hirachy_up(
    lowestids: str, hirachy_frame: pd.DataFrame = ALL_REGIONS
) -> pd.DataFrame:
    """[summary]

    :param lowestids: [description]
    :type lowestids: str
    :param hirachy_frame: [description], defaults to ALL_REGIONS
    :type hirachy_frame: pd.DataFrame, optional
    :raises RuntimeError: [description]
    :raises RuntimeError: [description]
    :return: [description]
    :rtype: pd.DataFrame
    """
    anscestors = []
    current_ids = lowestids
    while len(current_ids) > 0:
        current_regions = hirachy_frame.query("index.isin(@current_ids)")
        anscestors.append(current_regions)
        current_ids = current_regions.dropna().parent.unique()
    return pd.concat(anscestors).sort_index()


def hirachy_down(
    highest_ids: str,
    lowest_level: str = "lau",
    hirachy_frame: pd.DataFrame = ALL_REGIONS,
) -> pd.DataFrame:
    """[summary]

    :param highest_ids: [description]
    :type highest_ids: str
    :param lowest_level: [description], defaults to "lau"
    :type lowest_level: str, optional
    :param hirachy_frame: [description], defaults to ALL_REGIONS
    :type hirachy_frame: pd.DataFrame, optional
    :raises RuntimeError: [description]
    :raises RuntimeError: [description]
    :return: [description]
    :rtype: pd.DataFrame
    """
    descendents = [hirachy_frame.query("index.isin(@highest_ids)")]
    current_ids = highest_ids
    while len(current_ids) > 0:
        current_regions = hirachy_frame.query("parent.isin(@current_ids)")
        descendents.append(current_regions)
        current_ids = current_regions.dropna().index.unique()
        if lowest_level in current_regions.level.unique():
            break
    return pd.concat(descendents).sort_index()


def siblings(
    region_id: pd.DataFrame, hirachy_frame: pd.DataFrame = ALL_REGIONS
) -> pd.DataFrame:
    """[summary]

    :param region_id: [description]
    :type region_id: pd.DataFrame
    :param hirachy_frame: [description], defaults to ALL_REGIONS
    :type hirachy_frame: pd.DataFrame, optional
    :raises RuntimeError: [description]
    :raises RuntimeError: [description]
    :return: [description]
    :rtype: pd.DataFrame
    """
    parent = (  # noqa: F841
        hirachy_frame.query("index == @region_id").loc[:, "parent"].iloc[0]
    )
    return hirachy_frame.query("parent == @parent")


def get_regions() -> pd.DataFrame:
    """List of all the regions and their hierachy structure.

    This function returns a DataFrame of all the regions.
    It contains the name of the region and the its id.
    The latter is required to build queries. Additionally
    information is provided regarding the hierachy structure by
    listing the parent region for each region. Furthermore
    the regions statistical classification (nuts/lau) is provided.
    To allow for more filter options.

    For performance reasons this is simply read from disk.
    The regions are not expected to change significantly over time.
    Nonetheless an up to date DataFrame can be obtained with
    download_all_regions

    :return: DataFrame with all regions.
    """
    return ALL_REGIONS.copy()


state_regions: pd.DataFrame = get_regions().query('level == "nuts1"')
federal_state_dictionary = {
    region.name.replace("-", "_"): region.Index for region in state_regions.itertuples()
}

federal_states = ConfigMapping(federal_state_dictionary)


def get_statistics(
    search: Optional[str] = None,
    stat_meta_data_provider=None,
    target_language: str = "de",
    translation_provider: TranslationProvider = None,
) -> pd.DataFrame:
    """List of all the currently available statistics.

    This frunction returns a DataFrame of all available statistics.
    It contains the statistic code, which is required by the queries.
    It also contains a short and a long description of each statistic.
    By default it returns all available statistics, but it also
    has to option to provide a search keyword in advance.

    The original statistic description are in Germna, but the function
    also allows to get a machine translated version for english of these
    descritpions.

    :param search: Search term used for non-case-sensitive
        search in the long description
    :param translation_provider: Object used for translating the statistics.
        Defaults to  default translation provider if None
    :param target_language: language to translate statistic descriptions to,
        Possible values are currently 'de', 'en' for the default translation
        provider.
    :param stat_meta_data_provider: Source object used to obtain the
        statistic descriptions. Uses global default if missing.
    :return: Table with available statistics.
    """
    if stat_meta_data_provider is None:
        stat_meta_data_provider = DEFAULT_STATISTICS_META_DATA_PROVIDER

    if translation_provider is None:
        translation_provider = DEFAULT_TRANSLATION_PROVIDER

    if target_language != "de" and not translation_provider.is_valid_language_code(
        target_language
    ):
        valid_language_codes = str(translation_provider.get_valid_language_codes())
        raise ValueError(
            "Target language {0} is invalid or not available for translation provider, "
            "please use one of {1}".format(target_language, valid_language_codes)
        )

    stat_descr = stat_meta_data_provider.get_stat_descriptions()

    stat_frame = pd.DataFrame(
        [(stat, *stat_descr[stat]) for stat in stat_descr],
        columns=["statistic", "short_description", "long_description"],
    ).set_index("statistic")

    if target_language != "de":
        translation_provider.translate_data_frame_from_german(
            stat_frame, target_language
        )

    if search is not None:
        search_string = cast(str, search)  # noqa: F841
        return stat_frame.query(
            "short_description.str.contains(@search_string,case=False)"
        )
    else:
        return stat_frame


def get_availability_summary() -> pd.DataFrame:
    """Summary of available data for region/statistic combinations.

    There are many regions and statistics available within the
    datenguide API/at the original sources. Nonetheless data is not
    available for all combinations of statistics and regions.
    Furthermore some statistics might have been discontinued after
    a certain point in time.

    To help with the search for available statistics the function
    proved results from and availablility analysis for all
    statistics and all regions for nuts1, nuts2 and nuts3.
    This function returns the results of this analysis and contains
    for each analyzed region/statistic pair the corresponding
    id/code, the number of entries in the database and if applicable
    the first and last year when this statistic appeared.

    The function does not contain an overview of the lau regions
    and it does not contain an overview of possible drilldowns
    in statstics. For instance is the statstic available for men
    and women individually on top of its availability for the
    combined population.


    :return: Table with available statistics.
    """

    path = os.path.join(PACKAGE_DATA_PATH, "overview.csv")
    return pd.read_csv(path, converters={"region_id": lambda x: str(x)}).set_index(
        ["region_id", "statistic"]
    )


def download_all_regions() -> pd.DataFrame:
    """Downloads all current regions and their hierarchy structure.

    :raises RuntimeError: [description]
    :raises RuntimeError: [description]
    :return: [description]
    :rtype: pd.DataFrame
    """

    def nuts_query(nuts_level):
        q = Query.all_regions(nuts=nuts_level)
        return q

    def lau_query(lau_level):
        q = Query.all_regions(lau=lau_level)
        return q

    qb_all = Query.all_regions()

    qe = QueryExecutioner()
    print("start")
    all_regions = qe.run_query(qb_all)
    print("all")
    r_nuts1 = qe.run_query(nuts_query(1))
    print("nuts1")
    r_nuts2 = qe.run_query(nuts_query(2))
    print("nuts2")
    r_nuts3 = qe.run_query(nuts_query(3))
    print("nuts3")
    r_lau1 = qe.run_query(lau_query(1))
    print("lau")
    # currently no distinction between different laus
    # on datenguide side
    # r_lau2 = qe.run_query(lau_query(2))

    levels = {
        "nuts1": r_nuts1,
        "nuts2": r_nuts2,
        "nuts3": r_nuts3,
        "lau": r_lau1,
        # 'lau2':r_lau2
    }

    def isAnscestor(region_id, candidate):
        """[summary]

        :param region_id: [description]
        :type region_id: [type]
        :param candidate: [description]
        :type candidate: [type]
        :return: [description]
        :rtype: [type]
        """
        return region_id.startswith(candidate) and candidate != region_id

    def parent(region_id, region_details):
        """[summary]

        :param region_id: [description]
        :type region_id: [type]
        :param region_details: [description]
        :type region_details: [type]
        :return: [description]
        :rtype: [type]
        """
        desc = region_details.assign(
            ansc=lambda df: df.index.map(lambda i: isAnscestor(region_id, i))
        ).query("ansc")
        max_lev = desc.level.max()  # noqa: F841
        parent_frame = desc.query("level == @max_lev")
        if not parent_frame.empty:
            return parent_frame.iloc[0, :].name
        else:
            None

    if all_regions is None:
        raise RuntimeError("Was not able to download all regions")

    for k in levels:
        if levels[k] is None:
            raise RuntimeError(f"Was not able to download {k} regions")

    all_regions_df = pd.concat(
        [
            pd.DataFrame(page["data"]["allRegions"]["regions"])
            for page in cast(List[ExecutionResults], all_regions)[0].query_results
        ]
    ).set_index("id")

    level_df = pd.concat(
        pd.concat(
            [
                pd.DataFrame(page["data"]["allRegions"]["regions"])
                for page in cast(List[ExecutionResults], levels[k])[0].query_results
            ]
        ).assign(level=k)
        for k in levels
    )

    all_rg_parents = all_regions_df.join(
        level_df.set_index("id").loc[:, "level"]
    ).assign(
        parent=lambda df: df.index.map(
            partial(
                parent,
                region_details=all_regions_df.assign(
                    level=lambda df: df.index.map(len)
                ),
            )
        )
    )
    all_rg_parents.loc[all_rg_parents.level == "nuts1", "parent"] = "DG"

    return all_rg_parents
