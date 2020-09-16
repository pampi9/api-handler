from openapi_schema_to_json_schema import to_json_schema


class Openapi2JsonConverter:
    @staticmethod
    def convert_open_api_specs_to_json_schema(schema):
        return to_json_schema(schema)
