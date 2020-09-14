import requests

from .ApiResponse import ApiResponse
from .ApiResponse import MockResponse
from .JsonHandler import JsonHandler
from ..exceptions import OpenApiDefinitionException
from ..exceptions.OpenApiDefinitionException import StatusCodeException
from ..exceptions.RequestException import IgnoredParameterException
from ..exceptions.RequestException import MissingRequiredParameterException
from ..exceptions.RequestException import RequestAbortedException


class ApiRequest:
    REQUEST_TYPES = ["get", "post", "put", "delete"]

    def __init__(self, server, endpoint_definition, endpoint):
        # Server
        self.server = server
        # Path
        self.endpoint = endpoint
        # Endpoint definition
        self.endpoint_definition = endpoint_definition
        # Request type
        self.request_type = None
        # Components definition
        self.components = None

    @staticmethod
    def create_request(api, endpoint, request_type):
        server = api.server
        endpoint_definition = api.get_endpoint_definition(endpoint, request_type)
        # Request type
        request = None
        if endpoint_definition is not None and request_type in ApiRequest.REQUEST_TYPES:
            if request_type == "post":
                request = ApiPostRequest(server, endpoint_definition, endpoint)
            elif request_type == "get":
                request = ApiGetRequest(server, endpoint_definition, endpoint)
            elif request_type == "put":
                request = ApiPutRequest(server, endpoint_definition, endpoint)
            elif request_type == "delete":
                request = ApiDeleteRequest(server, endpoint_definition, endpoint)
            if request is not None:
                request.request_type = request_type
                if "components" in api.resources:
                    request.components = api.resources["components"]
        return request

    def build_url(self, parameters=None):
        if self.server is not None and "url" in self.server and self.endpoint_definition is not None:
            args_in_query = self.get_request_params_query(parameters)
            if args_in_query is None:
                return "{}{}".format(self.server["url"], self.endpoint)
            else:
                return "{}{}?{}".format(self.server["url"], self.endpoint, args_in_query)
        return None

    def get_request_params_query(self, parameters=None):
        # Build chain of param string
        if parameters is None:
            parameters = {}
        args = []
        if "parameters" in self.endpoint_definition and self.endpoint_definition["parameters"] is not None:
            for parameter in self.endpoint_definition["parameters"]:
                # TODO: Handle parameter in header, path
                if parameter["in"] == "query":
                    arg = ApiRequest.get_formatted_param_in_query(parameters, parameter)
                    if arg is not None:
                        args.append(arg)
        if len(args) == 0:
            return None
        else:
            return "&".join(args)

    @staticmethod
    def get_formatted_param_in_query(parameters, parameter):
        # Build single param string
        try:
            ApiRequest.extract_parameter(parameters, parameter)
            return "{}={}".format(parameter["name"], parameters[parameter["name"]])
        except (MissingRequiredParameterException, IgnoredParameterException) as e:
            raise RequestAbortedException(str(e))

    @staticmethod
    def extract_parameter(parameters, parameter):
        if "required" in parameter and parameter["required"] and parameter["name"] not in parameters:
            raise MissingRequiredParameterException("Required parameter '{}' is missing!".format(parameter["name"]))
        elif parameter["name"] not in parameters:
            raise IgnoredParameterException("Parameter '{}' is ignored!".format(parameter["name"]))
        else:
            return {parameter["name"]: parameters[parameter["name"]]}

    def check_response(self, status_code):
        if status_code not in self.endpoint_definition["responses"]:
            raise OpenApiDefinitionException.StatusCodeException(
                "Status code {}:{}:{} is missing.".format(self.endpoint, self.request_type, status_code))

    def get_response_schema(self):
        pass

    def process_response(self, url, response, error_flag):
        # Process response
        api_response = ApiResponse(url, response, error=error_flag)
        output = api_response.to_object()
        # Generate schema
        try:
            if self.check_response(str(response.status_code)):
                schema = self.__get_response_schema_path(str(response.status_code), "application/json")
                schema["components"] = {}
                schema["components"]["schemas"] = self.components["schemas"]
                # Validate against schema
                if not JsonHandler.validate(output["response"]["Payload"], schema, "response"):
                    print("Response doesn't correspond to predefined schema! {}".format(
                        output["response"]["Payload"]))
            else:
                output["response"]["Payload"] = response.json()
        except StatusCodeException:
            print("No schema found for validation of status_code {}!".format(response.status_code))
        return output

    def __get_response_schema_path(self, status_code, result_type):
        if "responses" in self.endpoint_definition and status_code in self.endpoint_definition["responses"]:
            if "content" in self.endpoint_definition["responses"][status_code] \
                    and result_type in self.endpoint_definition["responses"][status_code]["content"]:
                return self.endpoint_definition["responses"][status_code]["content"][result_type]["schema"]
            else:
                print("Response type {} undefined!".format(result_type))
        else:
            print("Status code {} undefined!".format(status_code))
        return None


class ApiPostRequest(ApiRequest):
    def call(self, url, body=None, authentication=None):
        pass


class ApiGetRequest(ApiRequest):
    def call(self, url, body=None, authentication=None):
        if url is not None:
            try:
                response = requests.get(url=url, auth=authentication)
                error_flag = False
            except (requests.exceptions.InvalidURL, requests.exceptions.ConnectionError):
                # TODO: Adjust response for Exception handling
                response = MockResponse({}, 500)
                error_flag = True
#                api_response = ApiResponse(url, response, error=error_flag, error_message=str(ex))
#                output = api_response.to_object()
        else:
            response = None
            error_flag = True
        return self.process_response(url, response, error_flag)


class ApiPutRequest(ApiRequest):
    def call(self, url, body=None, authentication=None):
        pass


class ApiDeleteRequest(ApiRequest):
    def call(self, url, body=None, authentication=None):
        pass
