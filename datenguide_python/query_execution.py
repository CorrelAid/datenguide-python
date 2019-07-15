from typing import Dict, Any, cast, Optional, NamedTuple, List
import requests
import re

Json = Dict[str, Any]


class ExecutionResults(NamedTuple):
    query_results: Json
    meta_data: Json


class QueryExecutioner(object):
    REQUEST_HEADER: Dict[str, str] = {"Content-Type": "application/json"}
    endpoint: str = "https://api-next.datengui.de/graphql"

    _meta_data_query_json: Dict[str, str] = {
        "query": r"""{
          __type(name: "Region") {
            fields {
              name
              description
              args {
                name
              }
            }
          }
        }"""
    }

    def __init__(self, alternative_endpoint: Optional[str] = None) -> None:
        if alternative_endpoint:
            self.endpoint = cast(str, alternative_endpoint)

    def run_query(self, query) -> Optional[ExecutionResults]:
        query_json = self._generate_post_json(query)
        results = self._send_request(query_json)
        if results:
            raw_stat_meta = self._get_stats_meta_data()
            if raw_stat_meta:
                stat_descriptions = QueryExecutioner._create_stat_desc_dic(
                    cast(Json, raw_stat_meta)
                )
                meta = {
                    stat: stat_descriptions[stat]
                    for stat in stat_descriptions
                    if stat in query.get_fields()
                }
            else:
                meta = {"error": "META DATA COULD NOT BE LOADED"}
            return ExecutionResults(query_results=cast(Json, results), meta_data=meta)
        else:
            return None

    @staticmethod
    def _generate_post_json(query) -> Dict[str, str]:
        post_json = dict()
        post_json["query"] = query.get_graphql_query()
        return post_json

    def _send_request(self, query_json: Dict[str, str]) -> Optional[Json]:
        resp = requests.post(
            self.endpoint, headers=self.REQUEST_HEADER, json=query_json
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"No result, got HTML status code {resp.status_code}")
            return None

    def _get_stats_meta_data(self) -> Optional[Json]:
        return self._send_request(self._meta_data_query_json)

    @staticmethod
    def _process_stat_meta_data(raw_response: Json) -> List[Json]:
        def contains_statistic(args: List[Json]):
            any(arg["name"] == "statistics" for arg in args)

        return [
            field
            for field in raw_response["data"]["__type"]["fields"]
            if contains_statistic(field["args"])
        ]

    @staticmethod
    def _extract_main_description(description: str) -> str:
        match = re.match(r"^\*\*([^*]*)\*\*", description)
        if match:
            return match.group(1)
        else:
            return "NO DESCRIPTION FOUND"

    @staticmethod
    def _create_stat_desc_dic(raw_response: Json) -> Dict[str, str]:
        return dict(
            (
                field["name"],
                QueryExecutioner._extract_main_description(field["description"]),
            )
            for field in QueryExecutioner._process_stat_meta_data(raw_response)
        )
