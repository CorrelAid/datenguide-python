from typing import Dict, Any, cast, Optional, NamedTuple, List, Tuple
import requests
import re

Json = Dict[str, Any]


class ExecutionResults(NamedTuple):
    query_results: Json
    meta_data: Json


class TypeMetaData(NamedTuple):
    kind: str
    fields: Optional[Json]
    enum_values: Optional[Dict[str, str]]


class FieldMetaDict(dict):
    def get_return_type(self) -> str:
        if self["type"]["kind"] == "LIST":
            return self["type"]["ofType"]["name"]
        else:
            return self["type"]["name"]

    def get_arguments(self) -> Dict[str, Tuple[Optional[str], ...]]:
        def get_type_of(
            argument: Dict[str, Any]
        ) -> Tuple[Optional[str], Optional[str]]:
            if argument["type"]["ofType"]:
                return (
                    argument["type"]["ofType"]["kind"],
                    argument["type"]["ofType"]["name"],
                )
            else:
                return None, None

        return {
            cast(str, arg["name"]): (
                cast(Optional[str], arg.get("type", {}).get("kind", {})),
                cast(Optional[str], arg.get("type", {}).get("name")),
                *get_type_of(arg),
            )
            for arg in self["args"]
        }


class QueryExecutioner(object):
    REQUEST_HEADER: Dict[str, str] = {"Content-Type": "application/json"}
    endpoint: str = "https://api-next.datengui.de/graphql"

    _META_DATA_CACHE: Json = dict()

    _meta_type_info: str = """
        query TypeInfo($type: String!) {
          __type(name: $type) {
            kind
            enumValues {
              name
              description
            }
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

    @staticmethod
    def _pagination_json(page):
        return {"page": page, "itemsPerPage": 1000}

    def run_query(self, query) -> Optional[List[ExecutionResults]]:
        if "allRegions" in query.get_fields():
            results = []
            page = 0
            while True:
                query_json = self._generate_post_json(
                    query, self._pagination_json(page)
                )
                result_page = self._send_request(query_json)
                if result_page is None:
                    return None
                results.append(result_page)
                if (cast(Json, result_page)["data"]["allRegions"]["page"] + 1) * (
                    cast(Json, result_page)["data"]["allRegions"]["itemsPerPage"]
                ) >= cast(Json, result_page)["data"]["allRegions"]["total"]:
                    break
                else:
                    page += 1
        else:
            query_json = self._generate_post_json(query)
            single_result = self._send_request(query_json)
            if single_result is None:
                return None
            else:
                results = [single_result]

        if results:
            # Region type contains all the statistics fields
            stat_meta = self.get_type_info("Region")
            if stat_meta:
                stat_descriptions = self._create_stat_desc_dic(
                    # casting given "Regions" type
                    cast(Json, cast(TypeMetaData, stat_meta).fields)
                )
                meta = {
                    stat: stat_descriptions[stat]
                    for stat in stat_descriptions
                    if stat in query.get_fields()
                }
            else:
                meta = {"error": "META DATA COULD NOT BE LOADED"}
            return [ExecutionResults(query_results=cast(Json, results), meta_data=meta)]
        else:
            return None

    def get_type_info(
        self, graph_ql_type: str, verbose=False
    ) -> Optional[TypeMetaData]:
        """
            Returns a json which at top level is a dict with all the
            fields of the type
        """
        if graph_ql_type in self.__class__._META_DATA_CACHE:
            if verbose:
                print("use cache")
            return self.__class__._META_DATA_CACHE[graph_ql_type]
        variables = {"type": graph_ql_type}
        query_json: Json = {}
        query_json["query"] = self._meta_type_info
        query_json["variables"] = variables
        if verbose:
            print("query REST API")
        info = self._send_request(query_json)
        if info:
            type_kind = info["data"]["__type"]["kind"]

            if type_kind == "OBJECT":
                field_meta: Optional[Json] = {
                    f["name"]: FieldMetaDict(f)
                    for f in info["data"]["__type"]["fields"]
                }
            else:
                field_meta = None

            if type_kind == "ENUM":
                enum_vals: Optional[Dict[str, str]] = {
                    value["name"]: value["description"]
                    for value in info["data"]["__type"]["enumValues"]
                }
            else:
                enum_vals = None
            type_meta = TypeMetaData(type_kind, field_meta, enum_vals)
            self.__class__._META_DATA_CACHE[graph_ql_type] = type_meta
            return type_meta
        else:
            return None

    @staticmethod
    def _generate_post_json(
        query, variables: Optional[Dict[str, str]] = None
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
            print(self.endpoint)
            print(f"No result, got HTML status code {resp.status_code}")
            return None

    @staticmethod
    def _process_stat_meta_data(type_fields: Json) -> List[Json]:
        return [
            type_fields[name]
            for name in type_fields
            if "statistics" in type_fields[name].get_arguments()
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
