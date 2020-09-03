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
    assert result
    assert api.authentication is None


def test_constructor_authentication_missing_environ():
    """
    Test ApiConnector with missing environment variables
      and create_authentication
    """
    api = ApiConnector(RESOURCES["existing_api"], "HTTPBasicAuth")
    result = api.create_authentication(RESOURCES["username"], RESOURCES["password"])
    assert not result


def test_constructor_authentication_environ():
    """
    Test ApiConnector with required environment variables
      and create_authentication
    """
    api = ApiConnector(RESOURCES["existing_api"], "HTTPBasicAuth")
    os.environ[RESOURCES["username"]] = "user"
    os.environ[RESOURCES["password"]] = "pass"
    result = api.create_authentication(RESOURCES["username"], RESOURCES["password"])
    assert result
    assert api.authentication is not None


def test_select_server_by_description():
    """
    Test ApiConnector with required environment variables
      and create_authentication
    """
    api = ApiConnector(RESOURCES["existing_api"], "HTTPBasicAuth")
    os.environ[RESOURCES["username"]] = "user"
    os.environ[RESOURCES["password"]] = "pass"
    api.create_authentication(RESOURCES["username"], RESOURCES["password"])
    result = api.select_server_by_description("Sample API")
    assert result
    assert api.server == {"url": "http://url:1234/api/v1", "description": "Sample API"}


def test_url_building_no_params():
    api = ApiConnector(RESOURCES["existing_api"], "HTTPBasicAuth")
    endpoint = api.get_endpoint_definition("/GetItems", "get")
    assert ("responses" in endpoint)
    url = api.get_request_params(endpoint, ["test"])
    assert url is None


def test_url_building_params():
    api = ApiConnector(RESOURCES["existing_api"], "HTTPBasicAuth")
    endpoint = api.get_endpoint_definition("/GetItem", "get")
    assert ("responses" in endpoint)
    url = api.get_request_params(endpoint, {"id": "test"})
    assert url is not None


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
