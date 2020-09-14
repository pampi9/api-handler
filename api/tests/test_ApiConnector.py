from api.model.ApiConnector import ApiConnector

RESOURCES = {
    "existing_api": "tests/resources/Api.json",
    "existing_operations": "tests/resources/Api_operations.json",
    "username": "api_username",
    "password": "api_password"
}


def test_select_server_by_description_existing():
    """
    Test Selection of server (value of description found)
    """
    api = ApiConnector(RESOURCES["existing_api"])
    result = api.select_server_by_description("Sample API")
    assert result
    assert api.server == {"url": "http://url:1234/api/v1", "description": "Sample API"}


def test_select_server_by_description_missing():
    """
    Test Selection of server (value of description not found)
    """
    api = ApiConnector(RESOURCES["existing_api"])
    result = api.select_server_by_description("Missing API")
    assert not result
    assert api.server is None
