from typing import Optional, Union, List, Dict, Any, Tuple
from pandas import DataFrame
from datenguidepy.query_execution import QueryExecutioner, TypeMetaData
from datenguidepy.output_transformer import QueryOutputTransformer


class Field:
    """A field of a query that specifies a statistic or
    (another information, e.g. source) to query.
    The name of the field (mostly statistic), the filters (specified with args)
    and the desired output information (fields)
    are specified.

    :param name: Name of Field or statistic
    :type name: str
    :param field: desired output fields (e.g. value or year), defaults to []
    :type field: list, optional
    :param args: Filters for the desired field (e.g. year = 2017).
    If "ALL" is passed as a value, then results are returned for all possible subgroups.
    (e.g. for gender GES = "ALL" three data entris are returned - for
    male, female and summed for both.
    if the filter is not set, then only the summed result is returned.
    Except for year: this is by default returned for each year.), defaults to {}
    :type args: dict, optional
    :param parent_field: The field this field is attached to, defaults to None
    :type parent_field: class:`datenguidepy.Field`, optional
    :param default_fields: Wether default fields should be attached or not,
    defaults to True
    :type default_fields: bool, optional
    :param return_type: The graphQL return type of this field
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
    ):
        self.name = name
        self.parent_field = parent_field
        self.default_fields = default_fields
        # TODO: use name as default?
        self.return_type = return_type if return_type else name

        self.fields: Dict[str, "Field"] = {}

        for field in fields:
            self.add_field(field, default_fields=default_fields)

        if default_fields:

            # only add default values if field is a statistic
            all_fields = Query._region_fields.fields if Query._region_fields else {}

            # explicitly check if all_fields isn't empty for mypy
            if all_fields:

                if self.name in all_fields:
                    field_args = all_fields[self.name].get_arguments()

                    # check if fields contains argument "statistics"
                    # and thus is a statistic
                    if "statistics" in field_args:
                        self.fields["year"] = Field(
                            "year", return_type=self._get_return_type("year")
                        )
                        self.fields["value"] = Field(
                            "value", return_type=self._get_return_type("value")
                        )
                        self.fields["source"] = Field(
                            "source",
                            fields=[
                                "title_de",
                                "valid_from",
                                "periodicity",
                                "name",
                                "url",
                            ],
                            return_type=self._get_return_type("source"),
                        )

        self.args = args

    def _get_return_type(self, fieldname):
        return (
            QueryExecutioner()
            .get_type_info(self.return_type)
            .fields[fieldname]
            .get_return_type()
        )

    def add_field(
        self, field: Union[str, "Field"], default_fields: bool = None
    ) -> "Field":
        """Add a subfield to the field.

        :raises TypeError: If the added field is neither of type String nor Field.
        :return: the added field
        :rtype: class:`datenguidepy.Field`
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
            )
            return self.fields[field]

        field._set_return_type(self)
        field._set_parent_field(self)
        self.fields[field.name] = field
        return self.fields[field.name]

    def drop_field(self, field: str):
        """Drop an attached subfield of the field.

        :param field: The name of the field to be droped.
        :type field: str
        :return: The field without the subfield.
        :rtype: class:`datenguidepy.Field`
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

    def _get_fields_to_query(
        self, field: Union[str, "Field"], region_id: str = None
    ) -> str:
        substring = ""
        if isinstance(field, str):
            substring += field + " "
        elif isinstance(field, Field):
            substring += field.name + " "

            if field.args:
                # make copy, so original field id is not overwritten
                this_query_args = field.args

                if (field.args.get("id", None) is not None) & (region_id is not None):
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
        else:
            raise TypeError
        return substring

    def get_fields(self) -> List[str]:
        """Get all fields that are attached to this
        field or subfields of this field.

        :return: a list of all fields
        :rtype: List[str]
        """

        field_list = [self.name]
        for value in self.fields.values():
            field_list.extend(Field._get_fields_helper(value))
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

        kind: str = "kind:\n"
        meta = QueryExecutioner().get_type_info(self.name)
        if meta is not None:
            kind += meta.kind
        else:
            kind += "None"
        description = "description:\n" + str(self.description())
        arguments = "arguments:\n" + str(self.arguments_info())
        fields = "fields:\n" + str(self.fields_info())
        enum_values = "enum values:\n" + str(self.enum_info())
        print("\n\n".join([kind, description, arguments, fields, enum_values]))

    @staticmethod
    def _no_none_values(base_function, dict_content, sub_key) -> Optional[str]:
        if dict_content is None:
            return None
        value = getattr(dict_content, sub_key)
        if value is None:
            return None
        return base_function(value)

    def _arguments_info_helper(self, meta_fields) -> Optional[str]:
        args = meta_fields[self.name].get_arguments()
        arg_list = []
        for key, value in args.items():
            temp_arg = key + str(value)
            arg_list.append(temp_arg)
        return ", ".join(arg_list)

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
            meta = QueryExecutioner().get_type_info(parent.return_type)
            return Field._no_none_values(self._arguments_info_helper, meta, "fields")
        else:
            return None

    def _fields_info_helper(self, meta_fields) -> Optional[str]:
        return ", ".join(meta_fields.keys())

    def fields_info(self) -> Optional[str]:
        """Get information on possible fields for field.

        :return: Possible fields for the field as string
        :rtype: Optional[str]
        """

        meta = QueryExecutioner().get_type_info(self.name)
        return Field._no_none_values(self._fields_info_helper, meta, "fields")

    def _enum_info_helper(self, enum_meta) -> Optional[str]:
        enum_list = []
        for key, value in enum_meta.items():
            enum_list.append(key + ": " + value)
        return ", ".join(enum_list)

    def enum_info(self) -> Optional[str]:
        """Get information on possible enum vaules for field.

        :return:  Possible enum values for the field as string.
        :rtype: Optional[str]
        """

        meta = QueryExecutioner().get_type_info(self.name)
        return Field._no_none_values(self._enum_info_helper, meta, "enum_values")

    def _description_helper(self, meta_fields) -> Optional[str]:
        return QueryExecutioner._extract_main_description(
            meta_fields[self.name]["description"]
        )

    def description(self) -> Optional[str]:
        """Get description of field.

        :return: Description of the field as string.
        :rtype: Optional[str]
        """

        parent = self.parent_field
        if parent is not None:
            meta = QueryExecutioner().get_type_info(parent.return_type)
            return Field._no_none_values(self._description_helper, meta, "fields")
        else:
            return None

    @staticmethod
    def _get_fields_helper(field: Union[str, "Field"]) -> List[str]:
        field_list = []
        if isinstance(field, str):
            field_list.append(field)
        else:
            field_list.append(field.name)
            if field.fields:
                for value in field.fields.values():
                    field_list.extend(Field._get_fields_helper(value))
        return field_list


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

    # static variables based on QueryExecutioner

    # static variable with all subfields of "Query"
    _query_fields: Optional[TypeMetaData] = QueryExecutioner().get_type_info("Query")

    _return_type_region: str = ""
    _return_type_allreg: str = ""
    if _query_fields:

        # static variable with return type of "region"
        _return_type_region = (
            _query_fields.fields["region"].get_return_type()
            if _query_fields.fields
            else ""
        )

        # static variable with return type of "allRegions"
        _return_type_allreg = (
            _query_fields.fields["allRegions"].get_return_type()
            if _query_fields.fields
            else ""
        )

    # static variable with all subfields of "Region"
    _region_fields: Optional[TypeMetaData] = QueryExecutioner().get_type_info(
        _return_type_region
    )

    # static variable with all subfields of "allRegions"
    _allregions_fields: Optional[TypeMetaData] = QueryExecutioner().get_type_info(
        _return_type_allreg
    )

    # static variable with return type of field "regions"
    _return_type_regions: str = "Region"

    def __init__(
        self,
        start_field: Field,
        region_field: Field = None,
        default_fields: bool = True,
    ):
        self.start_field = start_field
        self.region_field = region_field

    @classmethod
    def region(
        cls,
        region: Union[str, List[str]],
        fields: List[Union[str, "Field"]] = [],
        default_fields: bool = True,
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
            )
        )

    @classmethod
    def all_regions(
        cls,
        fields: List[Union[str, "Field"]] = [],
        parent: str = None,
        nuts: int = None,
        lau: int = None,
        default_fields: bool = True,
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
        )

        # add fields page, itemsperPage and total for QueryExecutioner
        return cls(
            start_field=Field(
                "allRegions",
                fields=[regions, "page", "itemsPerPage", "total"],
                args=args,
                return_type=Query._return_type_allreg,
                default_fields=default_fields,
            ),
            region_field=regions,
        )

    def add_field(self, field: Union[str, Field], default_fields=None) -> Field:
        """Ad a field to the query.

        Arguments:
            field -- Field to be added.
            default_fields-- Wether default fields
        should be attached or not.

        Raises:
            RuntimeError: If the allRegions Query has
            no regions field a subfield can be attached to.

        Returns:
            Field -- The added field.
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

        Arguments:
            field -- The name of the field to be droped.

        Returns:
            Query -- the query without the dropped field.
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

        Returns:
            List -- the Query as a String.
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

        Returns:
            List -- a list field names.
        """
        return self.start_field.get_fields()

    def _get_fields_with_types(self) -> List[Tuple[str, str]]:
        """Get all fields of a query including their
        return type.

        Returns:
            List[Tuple[Str,Str]] -- a list of tuples with
            field names and their types.
        """
        return self.start_field._get_fields_with_types()

    def results(self) -> DataFrame:
        """Runs the query and returns a Pandas DataFrame with the results.

        Raises:
            RuntimeError: If the Query did not return any results.
            E.g. if the Query was ill-formed.

        Returns:
            DataFrame --
            A DataFrame with the queried data.
            If the query fails raise RuntimeError.
        """
        result = QueryExecutioner().run_query(self)
        if result:
            # TODO: adapt QueryOutputTransformer to process list of results
            return QueryOutputTransformer(result).transform()
        else:
            raise RuntimeError("No results could be returned for this Query.")

    def meta_data(self) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Runs the query and returns a Dict with the meta data of the queries results.

        Raises:
            RuntimeError: If the Query did not return any results.
            E.g. if the Query was ill-formed.

        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]]] --
            A Dict with the queried meta data.
            If the query fails raise RuntimeError.
        """
        result = QueryExecutioner().run_query(self)
        if result:
            # TODO: correct indexing?
            return result[0].meta_data
        else:
            raise RuntimeError("No results could be returned for this Query.")

    @staticmethod
    def get_info(field: str = None) -> Optional[TypeMetaData]:
        """Get information on a specific field.
        If field is not specified return meta data for
        all statistics that can be queried.

        Arguments:
            field -- the field to get information on. If None,
            then information on all possible fields of a query are
            returned.

        Returns:
            Optional[TypeMetaData] -- Response from QueryExecutioner on meta data info
        """
        if field:
            return QueryExecutioner().get_type_info(field)
        else:
            return QueryExecutioner().get_type_info(Query._return_type_region)
