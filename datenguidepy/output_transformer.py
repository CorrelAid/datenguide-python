import pandas as pd
from typing import Dict, List, Any, Set, Container, cast

from datenguidepy.query_execution import ExecutionResults


class QueryOutputTransformer:
    """[description]

    Arguments:
             query_response: List[ExecutionResults] --
             Accepts the return type of the query executioner
             in case a non None value was return.
             This is a list of ExecutionResults as some
             python querys may internally be converted into
             several GraphQL queries to be executed,
             returnning one result each.
    """

    def __init__(
        self, query_response: List[ExecutionResults]
    ):  # query_response_json: Dict[str, Any]):
        """[summary]

        Arguments:
            query_response_json (Dict[str, Any]) -- [description]
        """
        self.query_response = query_response

    @staticmethod
    def _convert_results_to_frame(executioner_result) -> pd.DataFrame:
        result_frames = []
        for single_query_response in executioner_result:
            for page in single_query_response.query_results:
                result_frames.append(
                    QueryOutputTransformer._convert_regions_to_frame(
                        page, single_query_response.meta_data
                    )
                )
        return pd.concat(result_frames)

    @staticmethod
    def _convert_regions_to_frame(
        query_page: Dict[str, Any], meta_data: Dict[str, str]
    ) -> pd.DataFrame:
        if "region" in query_page["data"]:
            return QueryOutputTransformer.convert_single_results_to_frame(
                query_page["data"]["region"], meta_data
            )
        elif "allRegions" in query_page["data"]:
            allRegions = []
            for region in query_page["data"]["allRegions"]["regions"]:
                allRegions.append(
                    QueryOutputTransformer.convert_single_results_to_frame(
                        region, meta_data
                    )
                )
            return pd.concat(allRegions)
        else:
            raise RuntimeError(
                "Only queries containing" + '"region" or "regions" can be transformed'
            )

    @staticmethod
    def convert_single_results_to_frame(
        region_json: Dict[str, Any], meta: Dict[str, str]
    ) -> pd.DataFrame:
        if "error" in meta["statistics"]:
            raise RuntimeError(
                "No statistics meta data present. Try rerunning the query"
            )
        statistic_frames = [
            QueryOutputTransformer._create_statistic_frame(region_json[stat])
            for stat in cast(Dict[str, str], meta["statistics"]).keys()
        ]

        joined_results, join_cols = QueryOutputTransformer._join_statistic_results(
            statistic_frames, list(cast(Dict[str, str], meta["statistics"]).keys())
        )
        column_order = QueryOutputTransformer._determine_column_order(
            joined_results, join_cols
        )
        general_fields = QueryOutputTransformer._get_general_fields(region_json, meta)
        for field in general_fields:
            joined_results[field] = region_json[field]

        return joined_results[general_fields + column_order]

    @staticmethod
    def _get_general_fields(
        region_json: Dict[str, Any], meta: Dict[str, str]
    ) -> List[str]:
        return [
            field
            for field in region_json
            if all(stat not in field for stat in meta.keys())
        ]

    @staticmethod
    def _create_statistic_frame(statistic_sub_json: Dict[str, Any]) -> pd.DataFrame:
        return pd.io.json.json_normalize(statistic_sub_json, sep="_", max_level=1)

    @staticmethod
    def _determine_join_columns(statistic_results: List[pd.DataFrame]) -> Set[str]:
        """
        Dertermines the columns over which to join
        multiple statistics data frames.
        Currently has hardcoded exclusion criteria
        to never join across columns containing "value"
        and "source". This is not expected to be a severe
        limmitation as such joins are considered corner cases
        and can be achieved by post-join filters should
        the need arise.
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
        result_frame = frame.copy()
        result_frame.columns = [
            prefix + "_" + col if col not in exceptions else col
            for col in result_frame.columns
        ]
        return result_frame

    @staticmethod
    def _join_statistic_results(
        statistic_results: List[pd.DataFrame], statistic_names: List[str]
    ) -> pd.DataFrame:
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
        """
        Determines a rearrangement of the DataFrames column list
        grouping all source columns to the right and other information
        particularly the statistics values to the left.

        Arguments:
            joinded_frame DataFrame -- DataFrame with columns for all the
            statistics from the executed query
            join_columns Set[str] -- The columns that where used for joining
            different statistics

        Returns:
            List[str] -- List of ordered columns
        """
        join_col_list = list(join_columns)
        value_columns = [col for col in joined_frame if "value" in col]
        remaining_cols = [
            col
            for col in joined_frame
            if col not in join_columns and col not in value_columns
        ]
        return join_col_list + value_columns + remaining_cols

    def transform(self) -> pd.DataFrame:
        """Transform the queries results into a Pandas DataFrame.

        Returns:
            DataFrame -- Returns a pandas DataFrame of the queries results.
        """
        output = self._convert_results_to_frame(self.query_response)
        return output
