from typing import Dict, Any, cast, Optional, NamedTuple, List, Tuple
import requests
import re

Json = Dict[str, Any]


class ExecutionResults(NamedTuple):
    query_results: Json
    meta_data: Json


class FieldMetaDict(dict):
    def get_return_type(self) -> str:
        if self["type"]["kind"] == "LIST":
            return self["type"]["ofType"]["name"]
        else:
            return self["type"]["name"]

    def get_arguments(self) -> List[Tuple[Optional[str], ...]]:
        def get_type_of(
            argument: Dict[str, Any]
        ) -> Tuple[Optional[str], Optional[str]]:
            if argument["type"]["ofType"]:
                return (
                    argument["type"]["ofType"]["name"],
                    argument["type"]["ofType"]["kind"],
                )
            else:
                return None, None

        return list(
            (
                cast(Optional[str], arg.get("name")),
                cast(Optional[str], arg.get("type", {}).get("kind", {})),
                cast(Optional[str], arg.get("type", {}).get("name")),
                *get_type_of(arg),
            )
            for arg in self["args"]
        )

    def get_enumValues(self) -> List[Json]:
        return self["enumValues"]


class QueryExecutioner(object):
    REQUEST_HEADER: Dict[str, str] = {"Content-Type": "application/json"}
    endpoint: str = "https://api-next.datengui.de/graphql"

    _META_DATA_CACHE: Json = dict()

    _meta_type_info: str = """
        query TypeInfo($type: String!) {
      __type(name: $type) {
        fields {
          name
          enumValues
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

    def get_type_info(self, graph_ql_type: str) -> Optional[Json]:
        if graph_ql_type in self.__class__._META_DATA_CACHE:
            print("use cache")
            return self.__class__._META_DATA_CACHE[graph_ql_type]
        variables: Dict[str, str] = {"type": graph_ql_type}
        query_json: Json = {}
        query_json["query"] = self._meta_type_info
        query_json["variables"] = variables
        print("query database")
        info = self._send_request(query_json)
        if info:
            type_meta = {
                f["name"]: FieldMetaDict(f) for f in info["data"]["__type"]["fields"]
            }
            self.__class__._META_DATA_CACHE[graph_ql_type] = type_meta
            return type_meta
        else:
            return None

    @staticmethod
    def _generate_post_json(
        query, variables=Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        post_json: Json = dict()
        post_json["query"] = query.get_graphql_query()
        if variables:
            post_json["variables"] = cast(Dict[str, str], variables)
        return post_json

    def _send_request(self, query_json: Json) -> Optional[Json]:
        resp = requests.post(
            self.endpoint, headers=self.REQUEST_HEADER, json=query_json
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"No result, got HTML status code {resp.status_code}")
            return None

    def _get_stats_meta_data(self) -> Optional[Json]:
        return self.get_type_info("Region")

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
