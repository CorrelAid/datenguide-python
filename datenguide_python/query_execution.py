from typing import Dict, Any, cast, Optional, NamedTuple, List
import requests
import re

Json = Dict[str, Any]


class ExecutionResults(NamedTuple):
    query_results: Json
    meta_data: Json


class FieldMetaDict(dict):
    def get_return_type(self):
        if self["type"]["kind"] == "LIST":
            return self["type"]["ofType"]["name"]
        else:
            return self["type"]["name"]


class QueryExecutioner(object):
    REQUEST_HEADER: Dict[str, str] = {"Content-Type": "application/json"}
    endpoint: str = "https://api-next.datengui.de/graphql"

    _META_DATA_CACHE: Json = dict()

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

    _meta_type_info = """
        query TypeInfo($type: String!) {
      __type(name: $type) {
        fields {
          name
          type {
            ofType {
              name
            }
            kind
            name
            description
          }
          description
          args {
            name
            type {
              kind
              name
              ofType {
                name
                description
                kind
              }
            }
          }
        }
      }
    }
    """

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

    def _get_type_info(self, type):
        if type in self.__class__._META_DATA_CACHE:
            return self.__class__._META_DATA_CACHE[type]
        variables = {"type": type}
        query_json = {}
        query_json["query"] = self._meta_type_info
        query_json["variables"] = variables
        info = self._send_request(query_json)
        if info:
            type_meta = {
                f["name"]: FieldMetaDict(f) for f in info["data"]["__type"]["fields"]
            }
            self.__class__._META_DATA_CACHE[type] = type_meta
            return type_meta
        else:
            None

    @staticmethod
    def _generate_post_json(
        query, variables=Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        post_json = dict()
        post_json["query"] = query.get_graphql_query()
        if variables:
            post_json["variables"] = cast(Dict[str, str], variables)
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
            return any(arg["name"] == "statistics" for arg in args)

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
