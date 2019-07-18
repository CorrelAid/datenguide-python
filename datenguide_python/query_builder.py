from typing import NamedTuple, Optional


class QueryBuilder:
    def __init__(self, fields: list, region: str = None, parent: str = None):
        if region:
            self.region = region
        elif parent:
            self.parent = parent
        else:
            raise TypeError("region or parent must be defined.")
        # self.nuts =
        self.fields = fields
        # self.__dict__.update(kwargs)

    def _get_fields_to_query(self) -> str:
        fields_string = ""
        for field in self.fields:
            fields_string += self._get_fields_helper(field)
            # fields_string += "{" + " ".join(field.subfields) + "} "
        return fields_string.strip()

    def _get_fields_helper(self, field) -> str:
        substring = ""
        if isinstance(field, str):
            substring += field + " "
        elif isinstance(field, ComplexField):
            substring += field.field

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
            return (
                """
                    {
                        allRegions(page: $page, itemsPerPage:$itemsPerPage) {
                            regions(parent: \""""
                + self.parent
                + """\") {
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

    def get_fields(self) -> list:
        return self.fields


class ComplexField(NamedTuple):
    field: str
    subfields: list
    args: Optional[dict] = None
