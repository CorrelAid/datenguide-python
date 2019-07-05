class QueryBuilder():

    def __init__(self, region: str, fields: list):
        # must have region
        # filter for region: id

        # at least one subfield: fields
        # complex subfields
        # query: id, simple fields (id, name), complex fields (statistics with args(id, year, value, source, xx))
        # complex fields: (args, fields)

        # get_fields()

        self.region = region
        #self.nuts = 
        self.fields = fields
        # self.__dict__.update(kwargs)

    def _get_fields_to_query(self) -> str:
        fields_string = ""
        for field in self.fields:
            if isinstance(field, str):
                fields_string += field + " "
            elif isinstance(field, ComplexField):
                fields_string += field.statistic
                for key, value in field.filters.items():
                    fields_string += "(" + key + ": " + str(value) + ")"
                fields_string += "{" + " ".join(field.fields) + "} "

        print(fields_string)
        return fields_string

    def get_graphql_query(self) -> str:
        return """
                {
                    region(id: \"""" + self.region + """\") {
                        """ + self._get_fields_to_query() + """
                    }
                }
                """    

class ComplexField():

    def __init__(self, statistic, fields: list, filters: dict = None):
        self.statistic = statistic
        self.fields = fields
        self.filters = filters