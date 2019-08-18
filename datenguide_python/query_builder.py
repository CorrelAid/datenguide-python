from typing import Optional, Union, List, Dict
from datenguide_python.query_execution import (
    QueryExecutioner,
    TypeMetaData,
    ExecutionResults,
)


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
        args: Optional[Dict[str, str]] = None,
    ):

        self.name = name
        self.fields = fields
        self.args = args

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def add_field(self, field: Union[str, "Field"]) -> "Field":
        if isinstance(field, str):
            added_field = Field(name=field)
        else:
            added_field = field

        if self.fields:
            self.fields.append(added_field)
        else:
            self.fields = [added_field]
        return added_field

    def add_args(self, args: dict):
        if self.args:
            self.args.update(args)
        else:
            self.args = args

    def _get_fields_to_query(self, field: Union[str, "Field"]) -> str:
        substring = ""
        if isinstance(field, str):
            substring += field + " "
        elif isinstance(field, Field):
            substring += field.name

            if field.args:
                filters = []
                for key, value in field.args.items():
                    if value == "ALL":
                        filters.append("filter:{ " + key + ": { nin: []}}")
                    else:
                        # delete quotation marks for query arguments
                        filters.append(key + ": " + str(value).replace("'", ""))
                substring += "(" + ", ".join(filters) + ")"

            if field.fields:
                substring += "{"
                for subfield in field.fields:
                    substring += field._get_fields_to_query(subfield)
                substring += "}"
        else:
            raise TypeError
        return substring

    def get_fields(self):
        field_list = [self.name]
        for field in self.fields:
            field_list.extend(Field._get_fields_helper(field))
        return field_list

    def get_info(self) -> Optional[TypeMetaData]:
        return QueryExecutioner().get_type_info(self.name)

    @staticmethod
    def _get_fields_helper(field: Union[str, "Field"]) -> List[str]:
        field_list = []
        if isinstance(field, str):
            field_list.append(field)
        elif isinstance(field, Field):
            field_list.append(field.name)
            if field.fields:
                for subfield in field.fields:
                    field_list.extend(Field._get_fields_helper(subfield))
            else:
                raise TypeError
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

    def __init__(self, start_field: Field):
        """Initialize the Query with a start Field, which is either
        a region with a region ID or the field allRegions.

        Arguments:
            start_field {Field} -- The top node field.
            Either a single region or allRegions.
        """
        self.start_field = start_field

    @classmethod
    def regionQuery(
        cls, region: str, fields: List[Union[str, "Field"]] = []
    ) -> "Query":
        """Factory method to instantiate a Query with a single region through its region id.

        Arguments:
            region {str} -- The region id the statistics shall be queried for.
            fields {List[Union[str, Field]]} -- all fields that shall be returned
            for that region. Can either be simple fields (e.g. name)
            or fields with nested fields.

        Returns:
            Query -- A query object with region as start Field.
        """
        return cls(start_field=Field("region", fields, args={"id": '"' + region + '"'}))

    @classmethod
    def allRegionsQuery(
        cls,
        fields: List[Union[str, "Field"]] = [],
        parent: str = None,
        nuts: int = None,
        lau: int = None,
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

        regions = Field("regions", fields=fields, args=region_args)

        # add fields page, itemsperPage and total for QueryExecutioner
        return cls(
            start_field=Field(
                "allRegions",
                fields=[regions, "page", "itemsPerPage", "total"],
                args=args,
            )
        )

    def add_field(self, field: Union[str, Field]) -> Field:
        return self.start_field.add_field(field)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def get_graphql_query(self) -> str:
        """Formats the Query into a String that can be queried from the Datenguide API.

        Returns:
            str -- the Query as a String.
        """
        return "{" + self.start_field._get_fields_to_query(self.start_field) + "}"

    def get_fields(self) -> List[str]:
        """Get all fields of a query.

        Returns:
            List[Union[str, Field]] -- a list of strings and / or Fields
        """
        return self.start_field.get_fields()

    def results(self) -> Optional[ExecutionResults]:
        return QueryExecutioner().run_query(self)

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
            return QueryExecutioner().get_type_info("Region")
