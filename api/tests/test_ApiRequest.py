from api.exceptions.RequestException import MissingRequiredParameterException
from api.exceptions.RequestException import RequestAbortedException
from api.model.ApiConnector import ApiConnector
from api.model.ApiRequest import ApiRequest
from api.model.ApiResponse import MockResponse

RESOURCES = {
    "existing_api": "tests/resources/Api.json"
}


def create_api_request(endpoint, method_type="get", server_description="Sample API"):
    api = ApiConnector(RESOURCES["existing_api"])
    api.select_server_by_description(server_description)
    return ApiRequest.create_request(api, endpoint, method_type)


def test_build_get_request_missing_definition():
    """
    Test create of request
    """
    api_request = create_api_request("/GetItem_bad")
    assert api_request is None


def test_build_get_request_missing_parameter():
    """
    Test Building of URL
    """
    api_request = create_api_request("/GetItem")
    parameters = {"id": "my_id"}
    err_message = ""
    try:
        print(api_request.build_url(parameters))
    except RequestAbortedException as e:
        err_message = str(e)
    assert err_message == "Parameter 'name' is ignored!"


def test_build_get_request_all_required_parameters():
    """
    Test Building of URL
    """
    api_request = create_api_request("/GetItem")
    parameters = {"id": "my_id", "name": "my_name"}
    assert api_request.build_url(parameters) == "http://url:1234/api/v1/GetItem?id=my_id&name=my_name"


def test_build_get_request_with_no_parameters():
    """
    Test Building of URL
    """
    api_request = create_api_request("/GetItems")
    parameters = None
    assert api_request.build_url(parameters) == "http://url:1234/api/v1/GetItems"


def test_build_get_request_no_server():
    """
    Test Building of URL
    """
    api_request = create_api_request("/GetItems", server_description="")
    assert api_request.build_url() is None


def create_parameters():
    return {
        "parameter_from_definition": {
            "name": "id",
            "in": "query",
            "description": "Item Id",
            "required": True,
            "example": "item_id",
            "schema": {
                "type": "string"
            }
        }, "parameters": {"id": "my_id"}}


def test_extract_parameter():
    default = create_parameters()
    parameter_from_definition = default["parameter_from_definition"]
    parameters = default["parameters"]
    assert ApiRequest.extract_parameter(parameters, parameter_from_definition) == {'id': 'my_id'}


def test_extract_parameter_missing():
    default = create_parameters()
    parameter_from_definition = default["parameter_from_definition"]
    parameters = {}
    err_message = ""
    try:
        ApiRequest.extract_parameter(parameters, parameter_from_definition)
    except MissingRequiredParameterException as e:
        err_message = str(e)
    assert err_message == "Required parameter 'id' is missing!"


def test_get_formatted_param_in_query():
    default = create_parameters()
    parameter_from_definition = default["parameter_from_definition"]
    parameters = default["parameters"]
    assert ApiRequest.get_formatted_param_in_query(parameters, parameter_from_definition) == "id=my_id"


def test_get_request():
    api_request = create_api_request("/GetItem")
    parameters = {"id": "my_id", "name": "my_name"}
    url = api_request.build_url(parameters)
    response = api_request.call(url)
    print("url", url)
    print("response", response)
    assert response["status_code"] == 500
    assert response["response"]["StatusCode"] == 504
    assert response["response"]["Message"] == "Gateway timeout: "
    assert response["response"]["Payload"] == {}


def test_mock_response():
    api_request = ApiRequest(
        server=None,
        endpoint_definition={"responses": {"200": {}}},
        endpoint=None
    )

    response = MockResponse({"key1": "value1"}, 200)
    assert api_request.process_response("test_url", response, error_flag=False) == {
        'url': 'test_url', 'status_code': 200,
        'response': {'StatusCode': 200, 'Message': 'OK: dict', 'Payload': {'key1': 'value1'}}
    }

    response = MockResponse({}, 200)
    assert api_request.process_response("test_url", response, error_flag=False) == {
        'url': 'test_url', 'status_code': 200,
        'response': {'StatusCode': 200, 'Message': 'OK: dict', 'Payload': {}}
    }

    response = MockResponse([], 200)
    assert api_request.process_response("test_url", response, error_flag=False) == {
        'url': 'test_url', 'status_code': 200,
        'response': {'StatusCode': 200, 'Message': 'OK: list', 'Payload': []}
    }

    response = MockResponse("", 200)
    assert api_request.process_response("test_url", response, error_flag=False) == {
        'url': 'test_url', 'status_code': 200,
        'response': {'StatusCode': 204, 'Message': 'No content: empty response', 'Payload': ''}
    }
