from datenguidepy.query_builder import Query
from datenguidepy.query_execution import QueryExecutioner, ExecutionResults

from typing import Dict, Any, cast, Optional, List
import pandas as pd
from functools import partial

import os

dir_path = os.path.dirname(os.path.realpath(__file__))
ALL_REGIONS: pd.DataFrame = pd.read_csv(
    os.path.join(dir_path, "regions.csv"), index_col="id"
)


class ConfigMapping:
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
    parent = (  # noqa: F841
        hirachy_frame.query("index == @region_id").loc[:, "parent"].iloc[0]
    )
    return hirachy_frame.query("parent == @parent")


def get_all_regions() -> pd.DataFrame:
    """
        This function returns a DataFrame of all the regions.
        For performance reasons this is simply read from disk.
        The regions are not expected to change significantly over time.
        Nonetheless an up to date DataFrame can be obtained with
        download_all_regions
    """
    return ALL_REGIONS.copy()


state_regions: pd.DataFrame = get_all_regions().query('level == "nuts1"')
federal_state_dictionary = {
    region.name.replace("-", "_"): region.Index for region in state_regions.itertuples()
}

federal_states = ConfigMapping(federal_state_dictionary)


def get_statistics(search: Optional[str] = None) -> pd.DataFrame:
    stat_descr = QueryExecutioner().get_stat_descriptions()
    stat_frame = pd.DataFrame(
        [(stat, *stat_descr[stat]) for stat in stat_descr],
        columns=["statistics", "short_description", "long_description"],
    )
    if search is not None:
        search_string = cast(str, search)  # noqa: F841
        return stat_frame.query(
            "short_description.str.contains(@search_string,case=False)"
        )
    else:
        return stat_frame


def download_all_regions() -> pd.DataFrame:
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
    # on datehenguide side
    # r_lau2 = qe.run_query(lau_query(2))

    levels = {
        "nuts1": r_nuts1,
        "nuts2": r_nuts2,
        "nuts3": r_nuts3,
        "lau": r_lau1,
        # 'lau2':r_lau2
    }

    def isAnscestor(region_id, candidate):
        return region_id.startswith(candidate) and candidate != region_id

    def parent(region_id, region_details):
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
