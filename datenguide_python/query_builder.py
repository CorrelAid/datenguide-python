from typing import NamedTuple, Optional, Union, List, Dict


class Field(NamedTuple):
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

    name: str
    subfields: list
    args: Optional[Dict[str, Union[str, List[str]]]] = None


class QueryBuilder:
    def __init__(
        self,
        fields: List[Union[str, Field]],
        region: str = None,
        parent: str = None,
        nuts: int = None,
        lau: int = None,
    ):
        """Initialize the QueryBuilder either with a region or a parent region.

        Arguments:
            fields {List[Union[str, Field]]} -- all fields that shall be returned
            for that region. Can either be simple fields (e.g. name)
            or fields with nested fields.

        Keyword Arguments:
            region {str} -- The region the statistics shall be queried for.
            (default: {None})
            parent {str} -- The parent region the statistics shall be queried for.
            (default: {None})
            nuts {int} -- [The administration level: 1 – Bundesländer
            2 – Regierungsbezirke / statistische Regionen
            3 – Kreise / kreisfreie Städte.
            Default None returns results for all levels. (default: {None})
            lau {int} -- The administration level: 1 - Verwaltungsgemeinschaften
            2 - Gemeinden.
            Default returns results for all levels. (default: {None})

        Raises:
            TypeError: Region or parent must be defined.
            Raises TypeError if neither region or parent is specified.
        """

        if region:
            self.region = region
        elif parent:
            self.parent = parent
        else:
            raise TypeError("region or parent must be defined.")

        self.nuts = nuts if nuts else None
        self.lau = lau if lau else None
        self.fields = fields

    def _get_fields_to_query(self) -> str:
        fields_string = ""
        for field in self.fields:
            fields_string += self._get_fields_helper(field)
        return fields_string.strip()

    def _get_fields_helper(self, field) -> str:
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

            substring += "{"
            for subfield in field.subfields:
                substring += self._get_fields_helper(subfield)
            substring += "} "
        else:
            raise TypeError
        return substring

    def get_graphql_query(self) -> str:
        """Formats the QueryBuilder into a String that can be queried from the Datenguide API.

        Returns:
            str -- the Query as a String.
        """

        if hasattr(self, "region"):
            return (
                """
                {
                    region(id: \""""
                + self.region
                + """\") {
                        """
                + self._get_fields_to_query()
                + """
                    }
                }
                """
            )
        elif hasattr(self, "parent"):
            nuts = ""
            lau = ""
            if self.nuts:
                nuts = ", nuts: " + str(self.nuts)
            if self.lau:
                lau = ", lau: " + str(self.lau)
            return (
                """
                    {
                        allRegions(page: $page, itemsPerPage:$itemsPerPage) {
                            regions(parent: \""""
                + self.parent
                + '"'
                + nuts
                + lau
                + """) {
                                 """
                + self._get_fields_to_query()
                + """
                            }
                            page
                            itemsPerPage
                            total
                        }
                    }
                    """
            )
        else:
            raise TypeError("region or parent must be defined.")

    def get_fields(self) -> List[Union[str, Field]]:
        """Get all fields of a query.

        Returns:
            List[Union[str, Field]] -- a list of strings and / or Fields
        """
        return self.fields
