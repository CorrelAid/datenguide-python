class QueryBuilder():

    def __init__(self, region: str, fields: list):
        self.region = region
        #self.nuts = 
        self.fields = fields
        # self.__dict__.update(kwargs)

    def _get_fields_to_query(self) -> str:
        fields_string = ""
        for field in self.fields:
            fields_string += self._get_fields_helper(field)
            # fields_string += "{" + " ".join(field.subfields) + "} "
        return fields_string

    def _get_fields_helper(self, field) -> str:
        substring = ""
        if isinstance(field, str):
            substring += field + " "
        elif isinstance(field, ComplexField):
            substring += field.field

            if field.args:
                for key, value in field.args.items():
                    substring += "(" + key + ": " + str(value) + ")"
  
            substring += "{"
            for subfield in field.subfields:
                substring += self._get_fields_helper(subfield)
            substring += "} "
        else:
            raise TypeError
        return substring

    def get_graphql_query(self) -> str:
        return """
                {
                    region(id: \"""" + self.region + """\") {
                        """ + self._get_fields_to_query() + """
                    }
                }
                """    

    def get_fields(self) -> list:
        return self.fields


class ComplexField():

    def __init__(self, field, subfields: list, args: dict = None):
        self.field = field
        self.subfields = subfields
        self.args = args