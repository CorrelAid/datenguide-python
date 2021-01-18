from typing import Dict, Any, cast, Optional, NamedTuple, List, Tuple, Union
from typing_extensions import Protocol
import requests
import re

from datenguidepy.schema_json_meta import get_schema_json, get_json_path

Json_Dict = Dict[str, Any]
Json_List = List[Json_Dict]
Json = Union[Json_Dict, Json_List]

StatMeta = Dict[str, str]
UnitMeta = Dict[str, str]
EnumMeta = Dict[str, Dict[Optional[str], str]]
QueryResultsMeta = Dict[str, Union[StatMeta, EnumMeta, UnitMeta]]


class ExecutionResults(NamedTuple):
    """Results of a query with the results itself and the according meta data.
    """

    query_results: Json_List
    meta_data: QueryResultsMeta

    def contains_undefined_region_result(self):
        query_results_with_empty_region = list(
            filter(
                lambda query_result: query_result["data"]["region"] is None,
                self.query_results,
            )
        )
        return len(query_results_with_empty_region) > 0


class TypeMetaData(NamedTuple):
    """The meta data of a field, which consist of the kind, fields and enum values.
    """

    kind: str
    fields: Optional[Json_Dict]
    enum_values: Optional[Dict[str, str]]


class FieldMetaDict(dict):
    """[description]
    """

    def get_return_type(self) -> str:
        """Returns the return type of the field of the FieldMetaDict.

        :return: The return type of the field.
        :rtype: str
        """
        if self["type"]["kind"] == "LIST":
            return self["type"]["ofType"]["name"]
        else:
            return self["type"]["name"]

    def get_arguments(self) -> Dict[str, Tuple[Optional[str], ...]]:
        """[summary]

        :return: [description]
        :rtype: Dict[str, Tuple[Optional[str], ...]]
        """

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


def check_http200_body_error(body_json: Json_Dict) -> None:
    if "errors" in body_json:
        raise RuntimeError(
            "Body contains the following error content\n" + str(body_json)
        )


class GraphQlSchemaMetaDataProvider(object):
    """
        The GraphQlSchema meta data priovider helps to obtain
        meta data about the structure of the Graph QL api. As such
        it helps to privde information as to how structurally correct
        queries are build. It does not directly supply information
        about statistics.
    """

    endpoint: str = "https://api-next.datengui.de/graphql"

    REQUEST_HEADER: Dict[str, str] = {"Content-Type": "application/json"}

    _META_DATA_CACHE: Json_Dict = dict()

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

    def __init__(self, endpoint=None):
        if endpoint is not None:
            self.endpoint = endpoint

    def get_type_info(
        self, graph_ql_type: str, verbose=False
    ) -> Optional[TypeMetaData]:
        """Returns a json which at top level is a dict with all the
        fields of the type

        :param graph_ql_type: [description]
        :type graph_ql_type: str
        :param verbose: [description], defaults to False
        :type verbose: bool, optional
        :return: [description]
        :rtype: Optional[TypeMetaData]
        """

        if graph_ql_type in self.__class__._META_DATA_CACHE:
            if verbose:
                print("use cache")
            return self.__class__._META_DATA_CACHE[graph_ql_type]
        variables = {"type": graph_ql_type}
        query_json: Json_Dict = {}
        query_json["query"] = self._meta_type_info
        query_json["variables"] = variables
        if verbose:
            print("query REST API")
        info = self._send_request(query_json)
        if info:
            type_kind = info["data"]["__type"]["kind"]

            if type_kind == "OBJECT":
                field_meta: Optional[Json_Dict] = {
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

    def _send_request(self, query_json: Json_Dict) -> Optional[Json_Dict]:
        resp = requests.post(
            self.endpoint, headers=self.REQUEST_HEADER, json=query_json
        )
        if resp.status_code == 200:
            body_json = resp.json()
            check_http200_body_error(body_json)
            return body_json
        else:
            raise RuntimeError(
                self.endpoint
                + "\n"
                + f"No result, got HTML status code {resp.status_code}"
            )


class StatisticsMetaDataProvider(Protocol):
    def get_query_stat_meta(
        self, query_fields_with_types: List[Tuple[str, str]]
    ) -> StatMeta:
        ...

    def get_query_enum_meta(
        self, query_fields_with_types: List[Tuple[str, str]]
    ) -> EnumMeta:
        ...

    def get_query_unit_meta(
        self, query_fields_with_types: List[Tuple[str, str]]
    ) -> UnitMeta:
        ...

    def get_stat_descriptions(self) -> Dict[str, Tuple[str, str]]:
        ...

    def is_statistic(self, stat_candidate: str) -> bool:
        ...


class StatisticsGraphQlMetaDataProvider(object):
    """
        Statistics meta data providers help to supply informations about details
        pertaining to certain statistics that can be obtained via the API. This
        type of meta information is not API specific and can be obtained from
        different sources.
        This particular data provider uses graphql meta data information to provide
        results.
    """

    def __init__(self, endpoint=None):
        self.schema_meta_data_provider = GraphQlSchemaMetaDataProvider(
            endpoint=endpoint
        )

    def get_query_stat_meta(
        self, query_fields_with_types: List[Tuple[str, str]]
    ) -> StatMeta:
        # Region type contains all the statistics fields
        query_fields = [
            field_with_type[0] for field_with_type in query_fields_with_types
        ]
        stat_descriptions = self.get_stat_descriptions()
        stat_meta = {
            stat: stat_descriptions[stat][0]
            for stat in stat_descriptions
            if stat in query_fields
        }
        return stat_meta

    def get_query_unit_meta(
        self, query_fields_with_types: List[Tuple[str, str]]
    ) -> StatMeta:
        return {
            stat: "StatisticsGraphQlMetaDataProvider does not provide unit information."
            for stat, ty in query_fields_with_types
            if self.is_statistic(stat)
        }

    def get_query_enum_meta(
        self, query_fields_with_types: List[Tuple[str, str]]
    ) -> EnumMeta:
        enum_meta: EnumMeta = {}
        for field, field_type in query_fields_with_types:
            type_info = self.schema_meta_data_provider.get_type_info(field_type)
            if type_info is None:
                enum_meta[field] = {"error": "ENUM META DATA COULD NOT BE LOADED"}
            if cast(TypeMetaData, type_info).kind == "ENUM":
                enum_meta[field] = cast(
                    Dict[Optional[str], str], cast(TypeMetaData, type_info).enum_values
                )
        return enum_meta

    @staticmethod
    def _process_stat_meta_data(type_fields: Json_Dict) -> List[Json_Dict]:
        return [
            type_fields[name]
            for name in type_fields
            if "statistics" in type_fields[name].get_arguments()
        ]

    @staticmethod
    def _extract_main_description(description: str) -> str:
        match = re.match(r"^\s*\*\*([^*]*)\*\*", description)
        if match:
            return match.group(1)
        else:
            return "NO DESCRIPTION FOUND"

    def get_stat_descriptions(self) -> Dict[str, Tuple[str, str]]:
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        stat_meta = self.schema_meta_data_provider.get_type_info("Region")
        if stat_meta:
            stat_descriptions = self._create_stat_desc_dic(
                # casting given "Regions" type
                cast(Json_Dict, cast(TypeMetaData, stat_meta).fields)
            )
            return stat_descriptions
        else:
            raise RuntimeError("Meta data provider was anable to fetch statistics")

    def is_statistic(self, stat_candidate: str) -> bool:
        return stat_candidate in self.get_stat_descriptions()

    @staticmethod
    def _create_stat_desc_dic(raw_response: Json_Dict) -> Dict[str, Tuple[str, str]]:
        return dict(
            (
                field["name"],
                (
                    StatisticsGraphQlMetaDataProvider._extract_main_description(
                        field["description"]
                    ),
                    field["description"],
                ),
            )
            for field in StatisticsGraphQlMetaDataProvider._process_stat_meta_data(
                raw_response
            )
        )


class StatisticsSchemaJsonMetaDataProvider(object):
    """
        Statistics meta data providers help to supply informations about details
        pertaining to certain statistics that can be obtained via the API. This
        type of meta information is not API specific and can be obtained from
        different sources.
        This particular data provider the hard copy of a schema file from the SOAP
        cubes that datenguide extracts fron GENESIS and transfers into their API.
    """

    def __init__(self):
        self._full_data_json = [get_schema_json()]

    @property
    def stat_names(self):
        return [
            k
            for stat in get_json_path(self._full_data_json, ["..", "measures"])
            for k in stat.keys()
        ]

    def get_query_stat_meta(
        self, query_fields_with_types: List[Tuple[str, str]]
    ) -> StatMeta:
        fields = [field for field, _ in query_fields_with_types]
        sd = self.get_stat_descriptions()
        return {stat: sd[stat][0] for stat in sd if stat in fields}

    def get_query_unit_meta(
        self, query_fields_with_types: List[Tuple[str, str]]
    ) -> UnitMeta:

        fields = [field for field, _ in query_fields_with_types]

        units = self.get_stat_units()

        return {stat: units[stat] for stat in units if stat in fields}

    def get_query_enum_meta(
        self, query_fields_with_types: List[Tuple[str, str]]
    ) -> EnumMeta:
        enum_meta: EnumMeta = {}
        for field, _ in query_fields_with_types:
            enum_values = get_json_path(
                self._full_data_json,
                ["..", "measures", "..", "dimensions", field, "value_names"],
            )
            if len(enum_values) > 0:
                gesamt_update = {"GESAMT": "Gesamt"}
                enum_meta[field] = dict(enum_values[0], **gesamt_update)
        return enum_meta

    def is_statistic(self, stat_candidate: str) -> bool:
        return stat_candidate in self.stat_names

    def get_stat_units(self) -> Dict[str, str]:
        def get_unit_info(unit_json):
            return unit_json[0]["measure_name_de"]

        stat_names = get_json_path(
            self._full_data_json, ["..", "measures", "..", "name"]
        )
        units = map(
            get_unit_info,
            get_json_path(self._full_data_json, ["..", "measures", "..", "units"]),
        )
        return dict(zip(stat_names, units))

    def get_stat_descriptions(self) -> Dict[str, Tuple[str, str]]:

        stat_descriptions_short = get_json_path(
            self._full_data_json, ["..", "measures", "..", "title_de"]
        )
        stat_descriptions_long = get_json_path(
            self._full_data_json, ["..", "measures", "..", "definition_de"]
        )
        return {
            name: (short, long)
            for name, short, long in zip(
                self.stat_names, stat_descriptions_short, stat_descriptions_long
            )
        }

    def get_enum_values(self) -> Dict[str, Dict[str, str]]:
        names = get_json_path(
            self._full_data_json, ["..", "measures", "..", "dimensions", "..", "name"]
        )
        values = get_json_path(
            self._full_data_json,
            ["..", "measures", "..", "dimensions", "..", "value_names"],
        )
        gesamt_update = {"GESAMT": "Gesamt"}

        return {name: dict(vs, **gesamt_update) for name, vs in zip(names, values)}


DEFAULT_STATISTICS_META_DATA_PROVIDER = StatisticsSchemaJsonMetaDataProvider()


class QueryExecutioner(object):
    """Queries the Datenguide API for data and meta data.

    :param alternative_endpoint: [description], defaults to None
    :type alternative_endpoint: Optional[str], optional
    :return: [description]
    :rtype: None
    """

    REQUEST_HEADER: Dict[str, str] = {"Content-Type": "application/json"}
    endpoint: str = "https://api-next.datengui.de/graphql"

    def __init__(
        self,
        alternative_endpoint: Optional[str] = None,
        statistics_meta_data_provider=None,
    ) -> None:
        if alternative_endpoint:
            self.endpoint = cast(str, alternative_endpoint)

        self.graph_ql_schema_meta_data_provider = GraphQlSchemaMetaDataProvider(
            self.endpoint
        )

        if statistics_meta_data_provider is None:
            self.stat_meta_data_provider = DEFAULT_STATISTICS_META_DATA_PROVIDER
        else:
            self.stat_meta_data_provider = statistics_meta_data_provider

    def get_type_info(
        self, graph_ql_type: str, verbose=False
    ) -> Optional[TypeMetaData]:
        """Returns a json which at top level is a dict with all the
        fields of the type

        :param graph_ql_type: [description]
        :type graph_ql_type: str
        :param verbose: [description], defaults to False
        :type verbose: bool, optional
        :return: [description]
        :rtype: Optional[TypeMetaData]
        """
        return self.graph_ql_schema_meta_data_provider.get_type_info(
            graph_ql_type, verbose
        )

    @staticmethod
    def _pagination_json(page: int) -> Json_Dict:
        return {"page": page, "itemsPerPage": 1000}

    def run_query(self, query) -> Optional[List[ExecutionResults]]:
        """[summary]

        :param query: [description]
        :type query: [type]
        :return: [description]
        :rtype: Optional[List[ExecutionResults]]
        """
        all_results = [
            self._run_single_query_json(query_json, query._get_fields_with_types())
            for query_json in self._generate_post_json(query)
        ]
        if not any(map(lambda r: r is None, all_results)):
            return [cast(ExecutionResults, r) for r in all_results]
        else:
            return None

    def _run_single_query_json(
        self, query_json: Json_Dict, query_fields_with_types: List[Tuple[str, str]]
    ) -> Optional[ExecutionResults]:
        if "allRegions" in [
            field_with_types[0] for field_with_types in query_fields_with_types
        ]:
            results = []
            page = 0
            while True:
                query_json["variables"] = self._pagination_json(page)
                result_page = self._send_request(query_json)
                if result_page is None:
                    return None
                results.append(result_page)
                if (cast(Json_Dict, result_page)["data"]["allRegions"]["page"] + 1) * (
                    cast(Json_Dict, result_page)["data"]["allRegions"]["itemsPerPage"]
                ) >= cast(Json_Dict, result_page)["data"]["allRegions"]["total"]:
                    break
                else:
                    page += 1
        else:
            single_result = self._send_request(query_json)
            if single_result is None:
                return None
            else:
                results = [single_result]

        if results:
            meta: QueryResultsMeta = dict()
            meta["statistics"] = self.stat_meta_data_provider.get_query_stat_meta(
                query_fields_with_types
            )
            meta["enums"] = self.stat_meta_data_provider.get_query_enum_meta(
                query_fields_with_types
            )
            meta["units"] = self.stat_meta_data_provider.get_query_unit_meta(
                query_fields_with_types
            )
            return ExecutionResults(
                query_results=cast(Json_List, results), meta_data=meta
            )
            print(meta)
        else:
            return None

    @staticmethod
    def _generate_post_json(query) -> List[Dict[str, str]]:
        jsons: List[Dict[str, str]] = []
        for query_string in query.get_graphql_query():
            post_json: Json_Dict = dict()
            post_json["query"] = query_string
            jsons.append(post_json)
        return jsons

    def _send_request(self, query_json: Json_Dict) -> Optional[Json_Dict]:
        resp = requests.post(
            self.endpoint, headers=self.REQUEST_HEADER, json=query_json
        )
        if resp.status_code == 200:
            body_json = resp.json()
            check_http200_body_error(body_json)
            return body_json
        else:
            raise RuntimeError(
                self.endpoint
                + "\n"
                + f"No result, got HTML status code {resp.status_code}"
            )
