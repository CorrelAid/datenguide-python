from typing import NamedTuple, Optional, Union, List, Dict


class Field(NamedTuple):
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
        return self.fields
