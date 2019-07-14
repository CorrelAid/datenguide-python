from typing import Dict, Any, cast, Optional, NamedTuple
import requests

Json = Dict[str, Any]


class ExecutionResults(NamedTuple):
    query_results: Json
    meta_data: Json


class QueryExecutioner(object):
    REQUEST_HEADER: Dict[str, str] = {"Content-Type": "application/json"}
    endpoint: str = "https://api-next.datengui.de/graphql"

    def __init__(self, alternative_endpoint: Optional[str] = None) -> None:
        if alternative_endpoint:
            self.endpoint = cast(str, alternative_endpoint)

    def run_query(self, query) -> Optional[ExecutionResults]:
        query_json = self._generate_post_json(query)
        results = self._send_request(query_json)
        if results:
            return ExecutionResults(query_results=cast(Json, results), meta_data={})
        else:
            return None

    @staticmethod
    def _generate_post_json(query) -> Dict[str, str]:
        post_json = dict()
        post_json["query"] = query.get_graphql_str()
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
