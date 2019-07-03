class Query:

    def __init__(self, region: str, *args, **kwargs):
        # must have region
        # at least one subfield
        # args for subfields
        # id name and statistics possible as args

        # for statistics possible args: year, value, source, id, xxx

        self.region = region
        self.fields = kwargs
        # self.__dict__.update(kwargs)

    def get_graphql_query(self):
        # TODO: return all fields
        return """
                {
                    region(id:\"""" + self.region + """\") {
                        """ + " ".join(list(self.fields.values())) + """
                    }
                }
                """          