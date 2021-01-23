import numpy as np
import pandas as pd
from typing import Dict, List, Any, Set, Container, cast

from datenguidepy.query_execution import (
    ExecutionResults,
    StatMeta,
    EnumMeta,
    UnitMeta,
    QueryResultsMeta,
)
import copy


class QueryOutputTransformer:
    """Transforms the query results into a DataFrame.

        :param query_response: Accepts the return type of the query executioner
             in case a non None value was return.
             This is a list of ExecutionResults as some
             python querys may internally be converted into
             several GraphQL queries to be executed,
             returnning one result each.
        :type query_response: List[ExecutionResults]
        """

    def __init__(self, query_response: List[ExecutionResults]) -> None:

        self.query_response = query_response

    @staticmethod
    def _convert_results_to_frame(
        executioner_result: List[ExecutionResults], remove_duplicates: bool = False
    ) -> pd.DataFrame:
        """Converst raw query results to a DataFrame.

        This function converst thre return values from
        query_execution functinoality into a pandas DataFrame.

        :param executioner_result: Raw query results including meta data.
        :return: DataFrame with query results.
        """
        result_frames = []
        for single_query_response in executioner_result:
            for page in single_query_response.query_results:
                result_frames.append(
                    QueryOutputTransformer._convert_regions_to_frame(
                        page, single_query_response.meta_data, remove_duplicates
                    )
                )
        return pd.concat(result_frames)

    @staticmethod
    def _convert_regions_to_frame(
        query_page: Dict[str, Any],
        meta_data: QueryResultsMeta,
        remove_duplicates: bool = True,
    ) -> pd.DataFrame:
        """Converts and combines raw results for one or more regions.

        This result converts region output from the API. The
        Graphql API has two distinct enpoints, one called "region"
        returning results for a single region and one called "allRegions"
        which returns results for multiple regions. This function identifies
        the endpoint that was used and then converts the results for the one
        or more regions that it finds. If multiple regions are found,
        their results are concatenated.

        :param query_page: Single page of API query results as a python dict
            representation of a json.
        :meta_data: Query relevant meta data.
        :return: Converted results possible combined across multiple regions.
        """
        if "region" in query_page["data"]:
            return QueryOutputTransformer._convert_single_results_to_frame(
                query_page["data"]["region"], meta_data, remove_duplicates
            )
        elif "allRegions" in query_page["data"]:
            allRegions = []
            for region in query_page["data"]["allRegions"]["regions"]:
                allRegions.append(
                    QueryOutputTransformer._convert_single_results_to_frame(
                        region, meta_data, remove_duplicates
                    )
                )
            return pd.concat(allRegions)
        else:
            raise RuntimeError(
                "Only queries containing" + '"region" or "regions" can be transformed'
            )

    @staticmethod
    def _convert_single_results_to_frame(
        region_json: Dict[str, Any],
        meta: QueryResultsMeta,
        remove_duplicates: bool = False,
    ) -> pd.DataFrame:
        """Converts a region sub directory of raw output to a dataframe.

        This is the main internal method for converting raw API output
        to dataframes as results are composed of regions. This converts
        a single regions with the idea that results across regions
        can be concatenated. This function contains logic for joining
        data for several statistics in case more than one was queries.
        Furthermore the columns are conveniently sorted to put the most
        important information to the left.


        :param region_json: [description]
        :param meta: [description]
        :raises RuntimeError: The raised error is meant to cover the case
            where quert results were obtained but meta data wasn't possibly
            due to connection problems.
        :return: DataFrame with query results for a single region.
        """
        if "error" in meta["statistics"]:
            raise RuntimeError(
                "No statistics meta data present. Try rerunning the query"
            )
        statistic_frames = [
            QueryOutputTransformer._create_statistic_frame(region_json[stat])
            for stat in cast(StatMeta, meta["statistics"]).keys()
        ]
        if remove_duplicates:
            statistic_frames = [frame.drop_duplicates() for frame in statistic_frames]

        joined_results, join_cols = QueryOutputTransformer._join_statistic_results(
            statistic_frames, list(cast(StatMeta, meta["statistics"]).keys())
        )
        column_order = QueryOutputTransformer._determine_column_order(
            joined_results, join_cols
        )
        general_fields = QueryOutputTransformer._get_general_fields(
            region_json, cast(StatMeta, meta["statistics"])
        )
        for field in general_fields:
            joined_results[field] = region_json[field]

        renamed_results = QueryOutputTransformer._rename_statistic_fields(
            joined_results[general_fields + column_order],
            cast(StatMeta, meta["statistics"]),
        )

        return renamed_results

    @staticmethod
    def _get_general_fields(
        region_json: Dict[str, Any], stat_meta: Dict[str, str]
    ) -> List[str]:
        """Extract non statistic specific fields.

        For the purpouse of arranging dataframe columns this
        fuction extracts all dicionary fields that do not
        contain a statistic in their name.

        :param region_json: Dictionary for a specific region.
        :param stat_meta: Dictionary containg query meta data.
        :return: List of fields without statistics.
        """
        return [
            field
            for field in region_json
            if all(stat not in field for stat in stat_meta.keys())
        ]

    @staticmethod
    def _rename_statistic_fields(
        statistic_result: pd.DataFrame, stat_meta: Dict[str, str]
    ) -> pd.DataFrame:
        """Renames fields containing the statistic values.

        By default all statistic related fields are prefixed
        with the statistic name. As such the reported statistic
        itself has a column name STATISTIC_value. As the value
        is the most central column it is renamed into
        the the simple name STATISTIC.

        :param statistic_result: Results of a query.
        :param stat_meta: Meta data related to the query.
        :return: Results with renamed statistic column.
        """
        rename_mapping = {f"{stat}_value": stat for stat in stat_meta}
        return statistic_result.rename(columns=rename_mapping)

    @staticmethod
    def _create_statistic_frame(statistic_sub_json: Dict[str, Any]) -> pd.DataFrame:
        """Converst a json to a dataframe.

        This function converts the dictionary representation of a json
        to a pandas dataframe. Currenly this uses pandas directly.
        But it might be sensible to implement custom functionality as
        this function is the main reason for the pandas 1.0 requirement.

        :param statistic_sub_json: Python dictionary json representation.
        :return: Dataframe conversion of the dictionary.
        """
        return pd.json_normalize(statistic_sub_json, sep="_", max_level=1)

    @staticmethod
    def _determine_join_columns(statistic_results: List[pd.DataFrame]) -> Set[str]:
        """Dertermines join columns.

        When several statistics are queried this functino
        determines the columns over which to join
        multiple statistics data frames. This will typically
        lead to joining over the year column and enums
        that the statistics have in common.
        Currently has hardcoded exclusion criteria
        to never join across columns containing "value"
        and "source". This is not expected to be a severe
        limmitation as such joins are considered corner cases
        and can be achieved by post-join filters should
        the need arise.

        :param statistic_results: Dataframes for individual statistics
        :return: Columns over which to join.
        """
        candidates = {
            column
            for frame in statistic_results
            for column in frame
            if "value" not in column and "source" not in column
        }
        return {
            candidate
            for candidate in candidates
            if all(candidate in frame for frame in statistic_results)
        }

    @staticmethod
    def _prefix_frame_cols(
        frame: pd.DataFrame, prefix: str, exceptions: Container[str]
    ) -> pd.DataFrame:
        """Prefixes dataframe column names.

        This function prefixes dataframe column names with
        a given prefix but allows for exceptions to
        to be specified, i.e. columns that will not be prefixed.

        :param frame: Dataframe to be prefixed.
        :param prefix: Prefix to be used.
        :param exceptions: Columns that will not be prefixed.
        :return: Dataframe with prefixed columns.
        """
        result_frame = frame.copy()
        result_frame.columns = [
            prefix + "_" + col if col not in exceptions else col
            for col in result_frame.columns
        ]
        return result_frame

    @staticmethod
    def _join_statistic_results(
        statistic_results: List[pd.DataFrame], statistic_names: List[str]
    ) -> tuple:
        """Joins dataframes containing different statistics.

        When joining the frames, columns are first prefixed
        with statistic names.

        :param statistic_results: Dataframes with the statistics to be joined.
        :param statistic_names: Names of the statistics expected to be
            in the same order as the list of statistic results.
        :return: Joined frame and the columns over which was joined.
        """
        assert len(statistic_results) == len(statistic_names)

        join_columns = list(
            QueryOutputTransformer._determine_join_columns(statistic_results)
        )
        result = QueryOutputTransformer._prefix_frame_cols(
            statistic_results[0], statistic_names[0], join_columns
        )

        if len(statistic_results) == 1:
            return result, join_columns
        else:
            for statistic, name in zip(statistic_results[1:], statistic_names[1:]):
                result = result.merge(
                    QueryOutputTransformer._prefix_frame_cols(
                        statistic, name, join_columns
                    ),
                    on=join_columns,
                    how="outer",
                )
            return result, join_columns

    @staticmethod
    def _determine_column_order(
        joined_frame: pd.DataFrame, join_columns: Set[str]
    ) -> List[str]:
        """Determines column order for joined dataframe.

        This function determines a rearrangement of the DataFrame's
        column list, grouping all source columns to the right
        and other information particularly the
        statistics values to the left.

        :param joined_frame: DataFrame with columns for all the
            statistics from the executed query
        :type joined_frame: pd.DataFrame
        :param join_columns: The columns that where used for joining
            different statistics
        :type join_columns: Set[str]
        :return: List of ordered columns
        :rtype: List[str]
        """
        join_col_list = list(join_columns)
        value_columns = [col for col in joined_frame if "value" in col]
        source_cols = [col for col in joined_frame if "source" in col]
        remaining_cols = [
            col
            for col in joined_frame
            if col not in join_columns
            and col not in value_columns
            and col not in source_cols
        ]
        return join_col_list + value_columns + remaining_cols + source_cols

    @staticmethod
    def _make_verbose_statistic_names(
        output: pd.DataFrame, meta: QueryResultsMeta
    ) -> pd.DataFrame:
        """Exchanges statistic column names for short descriptions.

        By default statistic columns display the statistic code.
        This function converts the code to the short description,
        while keeping the code afterward. The aim is to make
        the dataframe more readable.

        :param output: Query results results after conversion to a dataframe.
        :param meta: Query meta data.
        :return: Dataframe with converted column names.
        """
        descriptions = cast(StatMeta, meta["statistics"])
        name_changes = {
            statistic: f"{descriptions[statistic]} ({statistic})"
            for statistic in descriptions
        }
        return output.rename(columns=name_changes)

    @staticmethod
    def _make_verbose_enum_values(
        output: pd.DataFrame, meta: QueryResultsMeta
    ) -> pd.DataFrame:
        """Exchanges enum codes for short descriptions.

        By default enum codes are displayed in enum columns.
        This function converts the codes to short descriptions.
        The aim is to make
        the dataframe more readable.

        :param output: Query results results after conversion to a dataframe.
        :param meta: Query meta data.
        :return: Dataframe with converted column names.
        """
        enum_mappings = copy.deepcopy(cast(EnumMeta, meta["enums"]))
        for enum in enum_mappings:
            enum_mappings[enum][None] = "Gesamt"
        mapped_frame = output.copy()
        for col, description_map in enum_mappings.items():
            if col in mapped_frame:
                mapped_frame[col] = mapped_frame[col].map(description_map)
            else:
                col_name = next(c for c in mapped_frame if c.endswith(col))
                mapped_frame[col_name] = mapped_frame[col_name].map(description_map)
        return mapped_frame

    @staticmethod
    def _add_units(output: pd.DataFrame, meta: QueryResultsMeta) -> pd.DataFrame:
        """Add units from meta_data to DataFrame.

        :param output: DataFrame with results
        :dtype output: pandas.DataFrame
        :param meta: Dictionary containing metadata for query.
        :dtype meta: QueryResultsMeta
        :return: Return DataFrame with results
        :dtype: pandas.DataFrame

        :raise NotImplementedError: More than one statistic in Query
        """

        def add_unit(statistic: str, unit: str):
            if not isinstance(unit, str):
                raise NotImplementedError("Unit is not a single string.")
            mask = output.columns.str.contains(statistic)
            position = int(np.argmax(mask))
            output.insert(loc=position + 1, column=f"{statistic}_unit", value=unit)

        # # ToDo: Uncertain if only one unit is possible per Statistic
        for statistic, unit in cast(UnitMeta, meta["units"].items()):
            add_unit(statistic, unit)
        return output

    def transform(
        self,
        verbose_statistic_names: bool = False,
        verbose_enum_values: bool = False,
        add_units: bool = False,
        remove_duplicates: bool = False,
    ) -> pd.DataFrame:
        """Transform the queries results into a Pandas DataFrame.

        This function allows for different flags that make
        the results more readable by using meta information
        about the query. By default the dataframe is not enrichted by meta
        information assuming an experienced user familiar with a particular statistic.
        For data exploration it is recommended to turn on one or more flags.

        :param verbose_statistic_names: Toggles statistic codes to short descriptions.
        :param verbose_enum_values: Toggles enum codes to descriptions if enum columns
            are present.
        :param add_units: Toggles the addition of a unit column for each statistic to
            make it easier to interpret the numbers.
        :param remove_duplicates: Removes duplicates from query results, i.e. if the
            exact same number has been reported for the same statistic, year, region
            etc. from the same source it gets removed. Such duplications are sometimes
            caused on the API side and this is convenience functionality to remove them.
            The removal happens before potentially joining several different statistics.
        :return: Returns a pandas DataFrame of the queries results.
        """
        output = self._convert_results_to_frame(self.query_response, remove_duplicates)
        if verbose_statistic_names:
            output = self._make_verbose_statistic_names(
                output, self.query_response[0].meta_data
            )
        if verbose_enum_values:
            output = self._make_verbose_enum_values(
                output, self.query_response[0].meta_data
            )
        if add_units:
            output = self._add_units(output, self.query_response[0].meta_data)
        return output
