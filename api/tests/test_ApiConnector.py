import os

from api.model.ApiConnector import ApiConnector
from api.model.ApiResponse import MockResponse

ApiConnector.UNIT_TEST = True

RESOURCES = {
    "existing_api": "tests/resources/Api.json",
    "existing_operations": "tests/resources/Api_operations.json",
    "username": "api_username",
    "password": "api_password"
}


def test_constructor_authentication_no_auth():
    """
    Test ApiConnector without auth
      and create_authentication
    """
    api = ApiConnector(RESOURCES["existing_api"])
    result = api.create_authentication(RESOURCES["username"], RESOURCES["password"])
    assert result == 0
    assert api.authentication is None


def test_constructor_authentication_missing_environ():
    """
    Test ApiConnector with missing environment variables
      and create_authentication
    """
    api = ApiConnector(RESOURCES["existing_api"], authentication="HTTPBasicAuth")
    result = api.create_authentication(RESOURCES["username"], RESOURCES["password"])
    assert (result == -1)


def test_constructor_authentication_environ():
    """
    Test ApiConnector with required environment variables
      and create_authentication
    """
    api = ApiConnector(RESOURCES["existing_api"], authentication="HTTPBasicAuth")
    os.environ[RESOURCES["username"]] = "user"
    os.environ[RESOURCES["password"]] = "pass"
    result = api.create_authentication(RESOURCES["username"], RESOURCES["password"])
    assert (result == 1)
    assert api.authentication is not None


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


def test_url_building_no_params_query():
    api = ApiConnector(RESOURCES["existing_api"])
    endpoint = api.get_endpoint_definition("/GetItems", "get")
    assert ("responses" in endpoint)
    url = api.get_request_params_query(endpoint, ["test"])
    assert url is None


def test_url_building_params_query():
    api = ApiConnector(RESOURCES["existing_api"])
    endpoint = api.get_endpoint_definition("/GetItem", "get")
    assert ("responses" in endpoint)
    url = api.get_request_params_query(endpoint, {"id": "test", "name": "my_name"})
    assert url is not None
    assert (url == "id=test&name=my_name")


def test_mock_response():
    response = MockResponse({"key1": "value1"}, 200)
    assert ApiConnector.process_response("test_url", response) == {
        'url': 'test_url', 'status_code': 200,
        'response': {'StatusCode': 1, 'Message': 'dict', 'Payload': {'key1': 'value1'}}
    }

    response = MockResponse({}, 200)
    assert ApiConnector.process_response("test_url", response) == {
        'url': 'test_url', 'status_code': 200,
        'response': {'StatusCode': 1, 'Message': 'dict', 'Payload': {}}
    }

    response = MockResponse([], 200)
    assert ApiConnector.process_response("test_url", response) == {
        'url': 'test_url', 'status_code': 200,
        'response': {'StatusCode': 1, 'Message': 'list', 'Payload': []}
    }

    response = MockResponse("", 200)
    assert ApiConnector.process_response("test_url", response) == {
        'url': 'test_url', 'status_code': 200,
        'response': {'StatusCode': 1, 'Message': '', 'Payload': ''}
    }
