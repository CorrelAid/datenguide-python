from typing import Optional, Union, List, Dict, Any
from pandas import DataFrame
from datenguide_python.query_execution import (
    QueryExecutioner,
    TypeMetaData,
    ExecutionResults,
)
from datenguide_python.output_transformer import QueryOutputTransformer


class Field:
    """A field of a query that specifies a statistic or
    (another information, e.g. source) to query.
    The name of the field (mostly statistic), the filters (specified with args)
    and the desired output information (subfields)
    are specified.

    Arguments:
        name {str} -- Name of Field or statistic
        subfields {list} -- desired output fields (e.g. value or year)
        args Optional[Dict[str, Union[str, List[str]]]] --
        Filters for the desired field (e.g. year = 2017).
        If "ALL" is passed as a value,
        then results are returned for all possible subgroups.
        (e.g. for gender GES = "ALL" the data for male,
        female and summed for both is returned.
        If the filter is not set, then only the summed result is returned.)
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
        self, field: Union[str, "Field"], default_fields: bool = True
    ) -> "Field":
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
        if isinstance(field, str):
            self.fields.pop(field, None)
        else:
            self.fields.pop(field.name, None)

    def add_args(self, args: dict):
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

    def get_fields(self):
        field_list = [self.name]
        for value in self.fields.values():
            field_list.extend(Field._get_fields_helper(value))
        return field_list

    def get_info(self) -> None:
        """Prints summarized information on a field's meta data.

        """
        kind: str = "kind: "
        meta = QueryExecutioner().get_type_info(self.name)
        if meta is not None:
            kind += meta.kind
        else:
            kind += "None"
        description = "description: " + str(self.description())
        arguments = "arguments: " + str(self.arguments_info())
        fields = "fields: " + str(self.fields_info())
        enum_values = "enum values: " + str(self.enum_info())
        print(
            kind
            + "\n"
            + description
            + "\n"
            + arguments
            + "\n"
            + fields
            + "\n"
            + enum_values
        )

    def arguments_info(self) -> Optional[str]:
        """Get information on possible arguments for field.

        Returns:
            str -- Possible arguments for the field as string.
        """
        parent = self.parent_field
        if parent is not None:
            meta = QueryExecutioner().get_type_info(parent.return_type)
            if meta is not None:
                meta_fields = meta.fields
                args = (
                    meta_fields[self.name]["args"]
                    if isinstance(meta_fields, dict)
                    else None
                )
                arg_list = []
                for i in range(0, len(args)):
                    temp_arg = str(args[i]["name"]) + " ["
                    temp_arg += (
                        str(args[i]["type"]["kind"]) + ":" if args[i]["type"] else ":"
                    )
                    temp_arg += (
                        str(args[i]["type"]["ofType"]["name"]) + "]"
                        if args[i]["type"]["ofType"]
                        else "]"
                    )
                    arg_list.append(temp_arg)
                return ", ".join(arg_list)
            else:
                return None
        else:
            return None

    def fields_info(self) -> Optional[str]:
        """Get information on possible fields for field.

        Returns:
            str -- Possible fields for the field as string.
        """
        meta = QueryExecutioner().get_type_info(self.name)
        if meta is not None:
            meta_fields = meta.fields
            if meta_fields is not None:
                return ", ".join(meta_fields.keys())
            else:
                return None
        else:
            return None

    def enum_info(self) -> Optional[str]:
        """Get information on possible enum vaules for field.

        Returns:
            str -- Possible enum values for the field as string.
        """
        enum_list = []
        meta = QueryExecutioner().get_type_info(self.name)
        if meta is not None:
            enum_meta = meta.enum_values
            if enum_meta:
                for key, value in enum_meta.items():
                    enum_list.append(key + ": " + value)
                return ", ".join(enum_list)
            else:
                return None
        else:
            return None

    def description(self) -> Optional[str]:
        """Get description of field.

        Returns:
            str -- Description of the field as string.
        """
        parent = self.parent_field
        if parent is not None:
            meta = QueryExecutioner().get_type_info(parent.return_type)
            if meta is not None:
                meta_fields = meta.fields
                if meta_fields is not None:
                    return QueryExecutioner._extract_main_description(
                        meta_fields[self.name]["description"]
                    )
                else:
                    return None
            else:
                return None
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

    Raises:
        TypeError: [description]
        TypeError: [description]
        TypeError: [description]

    Returns:
        [type] -- [description]
    """

    """static variables based on QueryExecutioner
    """
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
        """Initialize the Query with a start Field, which is either
        a region with a region ID or the field allRegions.

        Arguments:
            start_field {Field} -- The top node field (allRegions or Region).
            region_field {Field} -- If Top Node is allRegions
            then the second node is "regions" accessible through this field.

            Either a single region or allRegions.
        """
        self.start_field = start_field
        self.region_field = region_field

    @classmethod
    def regionQuery(
        cls,
        region: Union[str, List[str]],
        fields: List[Union[str, "Field"]] = [],
        default_fields: bool = True,
    ) -> "Query":
        """Factory method to instantiate a Query with a single region through its region id.

        Arguments:
            region {str} -- The region id the statistics shall be queried for.
            fields {List[Union[str, Field]]} -- all fields that shall be
            returned from the query
            for that region. Can either be simple fields (e.g. name)
            or fields with nested fields.

        Returns:
            Query -- A query object with region as start Field.
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
    def allRegionsQuery(
        cls,
        fields: List[Union[str, "Field"]] = [],
        parent: str = None,
        nuts: int = None,
        lau: int = None,
        default_fields: bool = True,
    ) -> "Query":
        """Factory method to instantiate a Query with allRegions start field.
        A parent id, nuts or lau can be further specified for the query.

        Arguments:
            fields {List[Union[str, Field]]} -- all fields that shall be returned
            for that region. Can either be simple fields (e.g. name)
            or fields with nested fields.
            parent {str} -- The region id of the parent region
            the statistics shall be queried for.
            (E.g. the id for a state where all sub regions within the
            state shall be queried for.)
            (default: {None})
            nuts {int} -- [The administration level: 1 – Bundesländer
            2 – Regierungsbezirke / statistische Regionen
            3 – Kreise / kreisfreie Städte.
            Default None returns results for all levels. (default: {None})
            lau {int} -- The administration level: 1 - Verwaltungsgemeinschaften
            2 - Gemeinden.
            Default returns results for all levels. (default: {None})

        Returns:
            Query -- A query object with allRegions as start Field.
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

    def add_field(self, field: Union[str, Field], default_fields=True) -> Field:
        if self.start_field.name == "allRegions":
            if self.region_field is not None:
                return self.region_field.add_field(field, default_fields=default_fields)
            else:
                raise TypeError("All Regions Query initialized without regions field.")
        else:
            return self.start_field.add_field(field, default_fields=default_fields)

    def drop_field(self, field: str) -> "Query":
        if self.start_field.name == "allRegions":
            if self.region_field is not None:
                self.region_field.drop_field(field)
                return self
            else:
                raise TypeError("All Regions Query initialized without regions field.")
        else:
            self.start_field.drop_field(field)
            return self

    def get_graphql_query(self) -> List[str]:
        """Formats the Query into a String that can be queried from the Datenguide API.

        Returns:
            str -- the Query as a String.
        """
        if self.start_field.name == "allRegions":
            query_prefix = "query ($page : Int, $itemsPerPage : Int) "
        else:
            query_prefix = ""

        # for regionQuery with multiple region IDs return a list of queries
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
            List[Union[str, Field]] -- a list of strings and / or Fields
        """
        return self.start_field.get_fields()

    def results(self) -> Union[DataFrame, Optional[ExecutionResults]]:
        """Runs the query and returns a Pandas DataFrame with the results.

        Raises:
            ValueError: If the Query did not return any results.
            E.g. if the Query was ill-formed.

        Returns:
            Union[DataFrame, Optional[ExecutionResults]] --
            A DataFrame with the queried data.
            If the query fails raise ValueError.
        """
        result = QueryExecutioner().run_query(self)
        if result:
            # TODO: adapt QueryOutputTransformer to process list of results
            return QueryOutputTransformer(result[0].query_results[0]).transform()
        else:
            raise ValueError("No results could be returned for this Query.")

    def meta_data(self) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Runs the query and returns a Dict with the meta data of the queries results.

        Raises:
            ValueError: If the Query did not return any results.
            E.g. if the Query was ill-formed.

        Returns:
            Union[DataFrame, Optional[ExecutionResults]] --
            A Dict with the queried meta data.
            If the query fails raise ValueError.
        """
        result = QueryExecutioner().run_query(self)
        if result:
            # TODO: correct indexing?
            return result[0].meta_data
        else:
            raise ValueError("No results could be returned for this Query.")

    @staticmethod
    def get_info(field: str = None) -> Optional[TypeMetaData]:
        """Get information on a specific field.
        If field is not specified return meta data for
        all statistics that can be queried.

        Returns:
            str -- Response from QueryExecutioner on meta data info
        """
        if field:
            return QueryExecutioner().get_type_info(field)
        else:
            return QueryExecutioner().get_type_info(Query._return_type_region)
