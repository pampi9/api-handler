from api.model.ApiOperations import ApiOperations
from api.model.JsonHandler import JsonHandler

RESOURCES = {
    "existing_api": "tests/resources/Api.json",
    "existing_operations": "tests/resources/Api_operations.json"
}


def test_constructor():
    """
    Test ApiOperations.read_json with missing file
    """
    config = JsonHandler.read_json(RESOURCES["existing_api"])
    api_operations = ApiOperations(config["paths"]["/GetItems"])
    expected = JsonHandler.read_json(RESOURCES["existing_operations"])
    assert api_operations.operations == expected
