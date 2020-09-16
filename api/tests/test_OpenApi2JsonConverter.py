from api.model.OpenApi2JsonConverter import Openapi2JsonConverter


def test_convert_openapi_to_json_schema():
    """
    Test Convert OpenApi to Json schema
    """
    openapi = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "FirstStation": {"type": "string", "nullable": True},
                "Guid": {"type": "string"},
                "LastStation": {"type": "string", "nullable": True},
                "ManufactureItem": {"type": "string", "nullable": True},
                "Name": {"type": "string"}
            }
        }
    }
    expected_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'FirstStation': {'type': ['string', 'null']},
                'Guid': {'type': 'string'},
                'LastStation': {'type': ['string', 'null']},
                'ManufactureItem': {'type': ['string', 'null']},
                'Name': {'type': 'string'}}
        },
        '$schema': 'http://json-schema.org/draft-04/schema#'
    }
    assert Openapi2JsonConverter.convert_open_api_specs_to_json_schema(openapi) == expected_schema
