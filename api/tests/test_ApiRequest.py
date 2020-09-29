from api.exceptions.RequestException import MissingRequiredParameterException
from api.exceptions.RequestException import RequestAbortedException
from api.model.ApiAuthentication import ApiAuthentication
from api.model.ApiConnector import ApiConnector
from api.model.ApiRequest import ApiRequest
from api.model.ApiResponse import MockResponse

RESOURCES = {
    "existing_api": "tests/resources/Api.json"
}
GET_ITEM_ENDPOINT = "/GetItem"
GET_ITEMS_ENDPOINT = "/GetItems"
MISSING_ENDPOINT = "/GetItem_bad"


def create_api_request(endpoint, method_type="get", server_description="Sample API"):
    api = ApiConnector(RESOURCES["existing_api"])
    api.select_server_by_description(server_description)
    return ApiRequest.create_request(api, endpoint, method_type)


def test_build_request_missing_definition():
    """
    Test create of request
    """
    # TODO: add put and delete request
    for method_type in ["get", "post"]:
        api_request = create_api_request(MISSING_ENDPOINT, method_type=method_type)
        assert api_request is None


def test_build_request_missing_parameter():
    """
    Test Building of URL
    """
    # TODO: add put and delete request
    for method_type in ["get", "post"]:
        api_request = create_api_request(GET_ITEM_ENDPOINT, method_type=method_type)
        parameters = {"id": "my_id"}
        err_message = ""
        try:
            print(api_request.build_url(parameters))
        except RequestAbortedException as e:
            err_message = str(e)
        assert err_message == "Parameter 'name' is ignored!"


def test_build_request_all_required_parameters():
    """
    Test Building of URL
    """
    # TODO: add put and delete request
    for method_type in ["get", "post"]:
        api_request = create_api_request(GET_ITEM_ENDPOINT, method_type=method_type)
        parameters = {"id": "my_id", "name": "my_name"}
        assert api_request.build_url(parameters) == "http://url:1234/api/v1/GetItem?id=my_id&name=my_name"


def test_build_request_with_no_parameters():
    """
    Test Building of URL
    """
    # TODO: add put and delete request
    for method_type in ["get", "post"]:
        api_request = create_api_request(GET_ITEMS_ENDPOINT, method_type=method_type)
        parameters = None
        assert api_request.build_url(parameters) == "http://url:1234/api/v1/GetItems"


def test_build_request_no_server():
    """
    Test Building of URL
    """
    # TODO: add put and delete request
    for method_type in ["get", "post"]:
        api_request = create_api_request(GET_ITEMS_ENDPOINT, server_description="", method_type=method_type)
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
    # TODO: add put and delete request
    for method_type in ["get", "post"]:
        api_request = create_api_request(GET_ITEM_ENDPOINT, method_type=method_type)
        parameters = {"id": "my_id", "name": "my_name"}
        url = api_request.build_url(parameters)
        response = api_request.call(url)
        print("url", url)
        print("response", response)
        assert response["status_code"] == 500
        assert response["response"]["StatusCode"] == 504
        assert response["response"]["Message"] == "Gateway timeout: "
        assert response["response"]["Payload"] == {}


def create_mock_response(response, datatype):
    if datatype in ["string", "object", "array"]:
        my_endpoint = {"responses": {
            "200": {
                "content": {
                    "application/json": {
                        "schema": {
                            "anyOf": [
                                {"type": datatype, "nullable": True}
                            ]
                        }
                    }
                }
            }
        }}
        api_request = ApiRequest(
            server=None,
            authentication=ApiAuthentication(),
            endpoint_definition=my_endpoint,
            endpoint=None
        )

        mock_response = MockResponse(response, 200)
        print(mock_response.json())
        return api_request.process_response("test_url", mock_response, error_flag=False)
    else:
        return None


def test_mock_response_dict():
    payload = {"key1": "value1"}
    assert create_mock_response(payload, "object") == {
        'url': 'test_url', 'status_code': 200,
        'response': {'StatusCode': 200, 'Message': 'OK: dict', 'Payload': payload}
    }


def test_mock_response_empty_dict():
    payload = {}
    assert create_mock_response(payload, "object") == {
        'url': 'test_url', 'status_code': 200,
        'response': {'StatusCode': 200, 'Message': 'OK: dict', 'Payload': payload}
    }


def test_mock_response_array():
    payload = []
    assert create_mock_response(payload, "array") == {
        'url': 'test_url', 'status_code': 200,
        'response': {'StatusCode': 200, 'Message': 'OK: list', 'Payload': payload}
    }


def test_mock_response_empty_string():
    payload = ""
    print(create_mock_response(payload, "string"))
    assert create_mock_response(payload, "string") == {
        'url': 'test_url', 'status_code': 200,
        'response': {'StatusCode': 204, 'Message': 'No content: empty response', 'Payload': payload}
    }
