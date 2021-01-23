from typing import Optional, Union, List, Dict, Any, Tuple, Set
from pandas import DataFrame
from datenguidepy.query_execution import (
    QueryExecutioner,
    GraphQlSchemaMetaDataProvider,
    StatisticsMetaDataProvider,
    DEFAULT_STATISTICS_META_DATA_PROVIDER,
    TypeMetaData,
    QueryResultsMeta,
)
from datenguidepy.output_transformer import QueryOutputTransformer


class Field:
    """A field of a query that specifies a statistic
    (or another information, e.g. source) to query.
    The name of the field (mostly statistic), the filters (specified with args)
    and the desired output information (fields)
    are specified.

    :param name: Name of Field (statistic)
    :type name: str
    :param fields: desired output fields (e.g. year or NAT), defaults to []
    :type fields: list, optional
    :param args: Filters for the desired field (e.g. {'year': 2017}).
    If "ALL" is passed as a value, then results are returned for all possible subgroups.
    (e.g. for gender 'GES': 'ALL' three data entries are returned - for
    male, female and summed for both.
    if the filter is not set, then only the summed result is returned.
    Except for year: this is by default returned for each year), defaults to {}
    :type args: dict, optional
    :param parent_field: The field this field is attached to, defaults to None
    :type parent_field: Field, optional
    :param default_fields: Wether default fields should be attached or not,
    defaults to True
    :type default_fields: bool, optional
    :param return_type: The graphQL return type of this field, defaults to None
    :type return_type: str, optional
    """

    def __init__(
        self,
        name: str,
        fields: List[Union[str, "Field"]] = [],
        args: Dict[str, Any] = {},
        parent_field: "Field" = None,
        default_fields: bool = True,
        return_type: str = None,
        stat_meta_data_provider: StatisticsMetaDataProvider = None,
    ):
        self.name = name
        self.parent_field = parent_field
        self.default_fields = default_fields
        # TODO: use name as default?
        self.return_type = return_type if return_type else name

        self.fields: Dict[str, "Field"] = {}
        if stat_meta_data_provider is None:
            self._stat_meta_data_provider: StatisticsMetaDataProvider = (
                DEFAULT_STATISTICS_META_DATA_PROVIDER
            )
        else:
            self._stat_meta_data_provider = stat_meta_data_provider

        self._graphql_schema_meta_data_provider = GraphQlSchemaMetaDataProvider()

        for field in fields:
            self.add_field(field, default_fields=default_fields)

        if default_fields and self._stat_meta_data_provider.is_statistic(self.name):

            self.fields["year"] = Field(
                "year", return_type=self._get_return_type("year")
            )
            self.fields["value"] = Field(
                "value", return_type=self._get_return_type("value")
            )
            self.fields["source"] = Field(
                "source",
                fields=["title_de", "valid_from", "periodicity", "name", "url"],
                return_type=self._get_return_type("source"),
            )

        self.args = args

    def _get_return_type(self, fieldname):
        return (
            self._graphql_schema_meta_data_provider.get_type_info(self.return_type)
            .fields[fieldname]
            .get_return_type()
        )

    def add_field(
        self, field: Union[str, "Field"], default_fields: bool = None
    ) -> "Field":
        """Add a subfield to the field.

        :raises TypeError: If the added field is neither of type String nor Field.
        :return: the added field
        :rtype: Field
        """
        if default_fields is None:
            default_fields = self.default_fields

        if isinstance(field, str):
            self.fields[field] = Field(
                name=field,
                parent_field=self,
                fields=[],
                return_type=self._get_return_type(field),
                default_fields=default_fields,
                stat_meta_data_provider=self._stat_meta_data_provider,
            )
            return self.fields[field]
        else:
            field._set_return_type(self)
            field._set_parent_field(self)
            field._stat_meta_data_provider = self._stat_meta_data_provider
            self.fields[field.name] = field
            return self.fields[field.name]

    def drop_field(self, field: str) -> "Field":
        """Drop an attached subfield of the field.

        :param field: The name of the field to be droped.
        :type field: str
        :return: The field without the subfield.
        :rtype: Field
        """
        if isinstance(field, str):
            self.fields.pop(field, None)
        else:
            self.fields.pop(field.name, None)
        return self

    def add_args(self, args: dict):
        """Add arguments to the field.
        :param args: Arguments to be added.
        :type args: dict
        """
        if self.args:
            self.args.update(args)
        else:
            self.args = args

    def _set_return_type(self, parentfield):
        self.return_type = parentfield._get_return_type(self.name)

    def _set_parent_field(self, parent_field):
        self.parent_field = parent_field

    def _get_fields_to_query(self, field: "Field", region_id: str = None) -> str:
        substring = field.name + " "

        if field.args:
            # make copy, so original field id is not overwritten
            this_query_args = field.args

            if ("id" in field.args) & (region_id is not None):
                # set region id to given single id to not use list
                this_query_args["id"] = region_id

            filters = []
            for key, value in this_query_args.items():
                if value == "ALL":
                    filters.append("filter:{ " + key + ": { nin: []}}")
                else:
                    # delete quotation marks for query arguments
                    filters.append(key + ": " + str(value).replace("'", ""))
            substring += "(" + ", ".join(filters) + ")"

        if field.fields:
            substring += "{"
            for field_item in field.fields.values():
                substring += field._get_fields_to_query(field_item)
            substring += "}"
        return substring

    def get_fields(self) -> List[str]:
        """Get all fields that are attached to this
        field or subfields of this field.

        :return: a list of all fields
        :rtype: List[str]
        """

        field_list = [self.name]
        for value in self.fields.values():
            field_list.extend(Field._get_fields_recursion(value))
        return field_list

    def _get_fields_with_types(self) -> List[Tuple[str, str]]:
        """ Gets all the fields and attached to
            this field including all subfields. Additionally
            returns the return type for each field. This will
            allow internal functions to easily reques meta
            data for specific fields.

            :return: a list of tuples with field names and
            their types
            :rtype: List[Tuple[str,str]]
        """
        fields_with_types = [(self.name, self.return_type)]
        for field in self.fields.values():
            fields_with_types.extend(field._get_fields_with_types())
        return fields_with_types

    def get_info(self) -> None:
        """Prints summarized information on a field's meta data.

        :return: None
        :rtype: None
        """

        kind: str = _bold_font("kind:") + "\n"
        meta = self._graphql_schema_meta_data_provider.get_type_info(self.name)
        if meta is not None:
            kind += meta.kind
        else:
            kind += "None"
        description = _bold_font("description:") + "\n" + str(self.description())
        arguments = _bold_font("arguments:") + "\n" + str(self.arguments_info())
        fields = _bold_font("fields:") + "\n" + str(self.fields_info())
        enum_values = _bold_font("enum values:") + "\n" + str(self.enum_info())
        print("\n\n".join([kind, description, arguments, fields, enum_values]))

    @staticmethod
    def _no_none_values(base_function, dict_content, sub_key) -> Optional[str]:
        if dict_content is None:
            return None
        value = getattr(dict_content, sub_key)
        if value is None:
            return None
        return base_function(value)

    def _arguments_info_formatter(self, meta_fields) -> Optional[str]:
        UNDERLINE = "\033[4m"
        NORMAL = "\033[0m"
        args = meta_fields[self.name].get_arguments()
        arg_list = []

        for key, value in args.items():

            single_arg_string = UNDERLINE + key + NORMAL + ": " + str(value[0])

            # get type
            if value[0] == "LIST":
                single_arg_string += (
                    " of type " + str(value[2]) + "(" + str(value[3]) + ")"
                )
            else:
                single_arg_string += "(" + str(value[1]) + ")"

            # get enum values
            if "ENUM" in value:
                args_field = Field(name=key, parent_field=self, return_type=value[3])
                enum_values = args_field.enum_info()
                single_arg_string += "\nenum values:\n" + str(enum_values)
            arg_list.append(single_arg_string)

        return "\n\n".join(arg_list)

    def arguments_info(self) -> Optional[str]:
        """Get information on possible arguments for field. The name of the argument is
        followed by the kind and name of the input type for the argument in brackets.
        If the argument is a list, the kind and name of the list elements are
        included in the brackets as well.

        :return: Possible arguments for the field as string and their input types.
        :rtype: Optional[str]
        """

        parent = self.parent_field
        if parent is not None:
            meta = self._graphql_schema_meta_data_provider.get_type_info(
                parent.return_type
            )
            return Field._no_none_values(self._arguments_info_formatter, meta, "fields")
        else:
            return None

    def _fields_info_formatter(self, meta_fields) -> Optional[str]:
        args_info = []
        for meta_field in meta_fields:
            args_info.append(meta_field + ": " + meta_fields[meta_field]["description"])
        return "\n".join(args_info)

    def fields_info(self) -> Optional[str]:
        """Get information on possible fields for field.

        :return: Possible fields for the field as string
        :rtype: Optional[str]
        """

        meta = self._graphql_schema_meta_data_provider.get_type_info(self.name)
        return Field._no_none_values(self._fields_info_formatter, meta, "fields")

    def _enum_info_formatter(self, enum_meta) -> Optional[str]:
        enum_list = []
        for key, value in enum_meta.items():
            enum_list.append(key + ": " + value)
        return "\n".join(enum_list)

    def enum_info(self) -> Optional[str]:
        """Get information on possible enum vaules for field.

        :return:  Possible enum values for the field as string.
        :rtype: Optional[str]
        """

        meta = self._graphql_schema_meta_data_provider.get_type_info(self.return_type)
        return Field._no_none_values(self._enum_info_formatter, meta, "enum_values")

    def description(self) -> Optional[str]:
        """Get description of field.

        :return: Description of the field as string.
        :rtype: Optional[str]
        """
        return self._stat_meta_data_provider.get_stat_descriptions()[self.name][0]

    @staticmethod
    def _get_fields_recursion(field: "Field") -> List[str]:
        field_list = []
        field_list.append(field.name)
        if field.fields:
            for value in field.fields.values():
                field_list.extend(Field._get_fields_recursion(value))
        return field_list


def _bold_font(text: str) -> str:
    BOLD = "\033[1m"
    NORMAL = "\033[0m"
    return BOLD + text + NORMAL


class Query:
    """A query to get information via the datenguide API for regionalstatistik.
    The query contains all fields and arguments.

    :param start_field: The top node field; either allRegions or Region.
    :type start_field: Field
    :param region_field: A field of type 'Region' that is needed
    if start_field is allRegions, defaults to None
    :type region_field: Field, optional
    :param default_fields: Wether default fields shall
            be attached to the fields., defaults to True
    :type default_fields: bool, optional
    :raises RuntimeError: [description]
    """

    # static variables specific to datenguide graphQL API
    _return_type_region: str = "Region"
    _return_type_allreg: str = "RegionsResult"
    _return_type_regions: str = "Region"

    def __init__(
        self,
        start_field: Field,
        region_field: Field = None,
        default_fields: bool = True,
        stat_meta_data_provider: StatisticsMetaDataProvider = None,
    ):
        self.start_field = start_field
        self.region_field = region_field
        self.result_meta_data: Optional[QueryResultsMeta] = None
        if stat_meta_data_provider is None:
            self._stat_meta_data_provider: StatisticsMetaDataProvider = (
                DEFAULT_STATISTICS_META_DATA_PROVIDER
            )
        else:
            self._stat_meta_data_provider = stat_meta_data_provider

        self._graphql_schema_meta_data_provider = GraphQlSchemaMetaDataProvider()

    @classmethod
    def region(
        cls,
        region: Union[str, List[str]],
        fields: List[Union[str, "Field"]] = [],
        default_fields: bool = True,
        stat_meta_data_provider=None,
    ) -> "Query":
        """Factory method to instantiate a Query with a single region through
            its region id.

        :param region: The region id(s) the statistics shall return
        :type region: Union[str, List[str]]
        :param fields: all fields that shall be
                returned from the query for that region.
                Can either be simple fields (e.g. name)
                or fields with nested fields.
        :type fields: list
                or fields with nested fields.
        :param default_fields: Wether default fields shall
        :type default_fields: bool

        :raises RuntimeError: [description]

        :return: A query object with region as start Field.
        :rtype: Query
        """

        if default_fields:
            defaults: List[Union[str, "Field"]] = ["id", "name"]
            fields = defaults + fields

        # add quotation marks around id for correct query
        if isinstance(region, list):
            region_arg: Union[str, List[str]] = [('"' + x + '"') for x in region]
        else:
            region_arg = ['"' + region + '"']

        return cls(
            start_field=Field(
                "region",
                fields,
                args={"id": region_arg},
                return_type=Query._return_type_region,
                default_fields=default_fields,
                stat_meta_data_provider=stat_meta_data_provider,
            ),
            stat_meta_data_provider=stat_meta_data_provider,
        )

    @classmethod
    def all_regions(
        cls,
        fields: List[Union[str, "Field"]] = [],
        parent: str = None,
        nuts: int = None,
        lau: int = None,
        default_fields: bool = True,
        stat_meta_data_provider=None,
    ) -> "Query":
        """Factory method to instantiate a Query with allRegions start field.
        A parent id, nuts or lau can be further specified for the query.

        :param fields: all fields that shall be returned
            for that region. Can either be simple fields (e.g. name)
            or fields with nested fields.
        :param parent: The region id of the parent region
            the statistics shall be queried for.
            (E.g. the id for a state where all sub regions within the
            state shall be queried for.)
        :type parent:
        :param nuts: The administration level: 1 – Bundesländer
            2 – Regierungsbezirke / statistische Regionen
            3 – Kreise / kreisfreie Städte.
            Default None returns results for all levels.
        :type nuts: int, optional
        :param lau: The administration level: 1 - Verwaltungsgemeinschaften
            2 - Gemeinden.
            Default returns results for all levels.
        :type lau: int, optional
        :type fields: list
        :param default_fields: Wether default fields shall
            be attached to the fields.
        :type default_fields: bool


        :return:  A query object with allRegions as start Field.
        :rtype: Query
        """

        # add page and itemsPerPage as arguments for QueryExecutioner
        args = {"page": "$page", "itemsPerPage": "$itemsPerPage"}

        region_args = {}
        if parent:
            region_args["parent"] = '"' + parent + '"'
        if nuts:
            region_args["nuts"] = str(nuts)
        if lau:
            region_args["lau"] = str(lau)

        if default_fields:
            defaults: List[Union[str, "Field"]] = ["id", "name"]
            fields = defaults + fields

        regions = Field(
            "regions",
            fields=fields,
            args=region_args,
            return_type=Query._return_type_regions,
            default_fields=default_fields,
            stat_meta_data_provider=stat_meta_data_provider,
        )

        # add fields page, itemsperPage and total for QueryExecutioner
        return cls(
            start_field=Field(
                "allRegions",
                fields=[regions, "page", "itemsPerPage", "total"],
                args=args,
                return_type=Query._return_type_allreg,
                default_fields=default_fields,
                stat_meta_data_provider=stat_meta_data_provider,
            ),
            region_field=regions,
            stat_meta_data_provider=stat_meta_data_provider,
        )

    def add_field(
        self, field: Union[str, Field], default_fields: bool = None
    ) -> "Field":
        """Add a field to the query.

        :param field: Field to be added
        :type field: Union[str, Field]
        :param default_fields: Wether default fields
        should be attached or not, defaults to None
        :type default_fields: bool, optional
        :raises RuntimeError: If the allRegions Query has
            no regions field a subfield can be attached to.
        :return: The added field.
        :rtype: Field
        """

        if default_fields is None:
            default_fields = self.start_field.default_fields

        if self.start_field.name == "allRegions":
            if self.region_field is not None:
                return self.region_field.add_field(field, default_fields=default_fields)
            else:
                raise RuntimeError(
                    "All Regions Query initialized without regions field."
                )
        else:
            return self.start_field.add_field(field, default_fields=default_fields)

    def drop_field(self, field: str) -> "Query":
        """Drop an attached field of the query.

        :param field: The name of the field to be droped
        :type field: str
        :raises RuntimeError: Raises Error if Query is
        initialized without regions field.
        :return: the query without the dropped field
        :rtype: Query
        """

        if self.start_field.name == "allRegions":
            if self.region_field is not None:
                self.region_field.drop_field(field)
                return self
            else:
                raise RuntimeError(
                    "All Regions Query initialized without regions field."
                )
        else:
            self.start_field.drop_field(field)
            return self

    def get_graphql_query(self) -> List[str]:
        """Formats the Query into a String that can be queried from the Datenguide API.

        :return: the Query formatted for the GraphQL API as a List of query strings
        :rtype: List[str]
        """
        if self.start_field.name == "allRegions":
            query_prefix = "query ($page : Int, $itemsPerPage : Int) "
        else:
            query_prefix = ""

        # for region with multiple region IDs return a list of queries
        if (self.start_field.name == "region") and isinstance(
            self.start_field.args.get("id", ""), list
        ):
            query_list: List[str] = []
            for region_id in self.start_field.args["id"]:
                query_list += [
                    (
                        "{"
                        + self.start_field._get_fields_to_query(
                            self.start_field, region_id
                        )
                        + "}"
                    )
                ]
            return query_list
        else:
            return [
                query_prefix
                + "{"
                + self.start_field._get_fields_to_query(self.start_field)
                + "}"
            ]

    def get_fields(self) -> List[str]:
        """Get all fields of a query.

        :return: a list field names
        :rtype: List[str]
        """
        return self.start_field.get_fields()

    def _get_fields_with_types(self) -> List[Tuple[str, str]]:
        """Get all fields of a query including their
        return type.

        :return: a list of tuples with
            field names and their types.
        :rtype: List[Tuple[str, str]]
        """
        return self.start_field._get_fields_with_types()

    def results(
        self,
        verbose_statistics: bool = False,
        verbose_enums: bool = False,
        add_units: bool = False,
        remove_duplicates: bool = True,
    ) -> DataFrame:
        """Runs the query and returns a Pandas DataFrame with the results.
           It also fills the instance variable result_meta_data with meta
           data specific to the query instance.

        :param verbose_statistics: Toggles whether statistic column names
            displayed with their short description in the result data frame
        :param verbose_enums: Toggles whether enum values are displayed
            with their short description in the result data frame
        :param add_units: Adds units available in the metadata to the
            result dataframe. Care should be taken, because not every
            statistic specifies these corretly. When in doubt one should
            refer to the statistic description.
        :param remove_duplicates: Removes duplicates from query results, i.e. if the
            exact same number has been reported for the same statistic, year, region
            etc. from the same source it gets removed. Such duplications are sometimes
            caused on the API side and this is convenience functionality to remove them.
            The removal happens before potentially joining several different statistics.
            Unless diagnosing the API the default (True) is generally in the users
            interest.

        :raises RuntimeError: If the query fails raise RuntimeError.
        :return: A DataFrame with the queried data.
        :rtype: DataFrame
        """
        if not self._contains_statistic_field():
            raise Exception(
                "No statistic field is defined in query, please add statistic field "
                "via method add_field."
            )

        result = QueryExecutioner(
            statistics_meta_data_provider=self._stat_meta_data_provider
        ).run_query(self)
        if result:
            # It is currently assumed that all graphql queries
            # that are generated internally for the Query instance
            # at hand yield the same meta data.
            if self._query_result_contains_undefined_region(result):
                raise ValueError("Queried region is invalid.")
            self.result_meta_data = result[0].meta_data
            return QueryOutputTransformer(result).transform(
                verbose_statistic_names=verbose_statistics,
                verbose_enum_values=verbose_enums,
                add_units=add_units,
                remove_duplicates=remove_duplicates,
            )
        else:
            raise RuntimeError("No results could be returned for this Query.")

    def _query_result_contains_undefined_region(self, result):
        return (
            len(
                list(filter(lambda res: res.contains_undefined_region_result(), result))
            )
            > 0
        )

    def _contains_statistic_field(self) -> bool:
        fields = self._get_all_field_names()
        contains_statistic = any(
            [self._stat_meta_data_provider.is_statistic(field) for field in fields]
        )
        return contains_statistic

    def _get_all_field_names(self) -> Set[str]:
        start_field_subfields = (
            set() if self.start_field is None else set(self.start_field.fields.keys())
        )
        region_field_subfields = (
            set() if self.region_field is None else set(self.region_field.fields.keys())
        )
        return start_field_subfields.union(region_field_subfields)

    def meta_data(self) -> QueryResultsMeta:
        """Runs the query and returns a Dict with the meta data of the queries results.

        :raises RuntimeError: If the Query did not return any results.
        E.g. if the Query was ill-formed.
        :return: A Dict with the queried meta data.
            If the query fails raise RuntimeError.
        :rtype: Union[Dict[str, Any], List[Dict[str, Any]]]
        """

        result = QueryExecutioner(
            statistics_meta_data_provider=self._stat_meta_data_provider
        ).run_query(self)
        if result:
            # TODO: correct indexing?
            return result[0].meta_data
        else:
            raise RuntimeError("No results could be returned for this Query.")

    def get_info(self, field: str = None) -> Optional[TypeMetaData]:
        """Get information on a specific field.
        If field is not specified return meta data for
        all statistics that can be queried.

        :param field: the field to get information on. If None,
            then information on all possible fields of a query are
            returned, defaults to None
        :type field: str, optional
        :return: Response from QueryExecutioner on meta data info
        :rtype: Optional[TypeMetaData]
        """
        if field:
            return self._graphql_schema_meta_data_provider.get_type_info(field)
        else:
            return self._graphql_schema_meta_data_provider.get_type_info(
                Query._return_type_region
            )
