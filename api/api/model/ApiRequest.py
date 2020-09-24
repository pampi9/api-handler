import requests

from .ApiResponse import ApiResponse
from .ApiResponse import MockResponse
from .JsonHandler import JsonHandler
from .OpenApi2JsonConverter import Openapi2JsonConverter
from ..exceptions import OpenApiDefinitionException
from ..exceptions import RequestException


class ApiRequest:
    """
    Abstract class for API requests, specific implementation is done in the inherited classes
    ApiPostRequest, ApiGetRequest, ApiDeleteRequest, ApiPutRequest
    """
    REQUEST_TYPES = ["get", "post", "put", "delete"]

    def __init__(self, server, authentication, endpoint_definition, endpoint):
        """
        ApiRequest constructor
        :param server: server bloc of ApiConnector {"url":<something>, "description":<something>}
        :param authentication: ApiAuthentication object
        :param endpoint_definition: one endpoint description out of the ApiConnector
        :param endpoint: endpoint key (string) from paths (OpenApi Specs)
        """
        # Server
        self.server = server
        # Authentication
        self.authentication = authentication
        # Path
        self.endpoint = endpoint
        # Endpoint definition
        self.endpoint_definition = endpoint_definition
        # Request type
        self.request_type = None
        # Components definition
        self.components = None
        # TODO: schema validation of parameters and body
        # "post": {
        #   "RequestBody": {
        #       "content": "application/json"
        #       "schema": {
        #           $ref: "#/components/schemas/User"
        #       }
        #   }

    @staticmethod
    def create_request(api, endpoint, request_type):
        """
        Static method for creating the request
        :param api: ApiConnector object
        :param endpoint: endpoint key (string) from paths (OpenApi Specs)
        :param request_type: type of request (second key level from paths[<endpoint>] in OpenApi Specs)
        :return: ApiRequest object
        """
        server = api.server
        endpoint_definition = api.get_endpoint_definition(endpoint, request_type)
        # Request type
        request = None
        if endpoint_definition is not None and request_type in ApiRequest.REQUEST_TYPES:
            if request_type == "post":
                request = ApiPostRequest(server, api.authentication, endpoint_definition, endpoint)
            elif request_type == "get":
                request = ApiGetRequest(server, api.authentication, endpoint_definition, endpoint)
            elif request_type == "put":
                request = ApiPutRequest(server, api.authentication, endpoint_definition, endpoint)
            elif request_type == "delete":
                request = ApiDeleteRequest(server, api.authentication, endpoint_definition, endpoint)
            if request is not None:
                request.request_type = request_type
                if "components" in api.resources:
                    request.components = api.resources["components"]
        return request

    def build_url(self, parameters=None):
        """
        Method to generate the URL with the parameters given in the arguments
        :param parameters: dict of parameters (parameter_name, parameter_value)
        :return: URL to invoke
        """
        if self.server is not None and "url" in self.server and self.endpoint_definition is not None:
            args_in_query = self.get_request_params_query(parameters)
            if args_in_query is None:
                return "{}{}".format(self.server["url"], self.endpoint)
            else:
                return "{}{}?{}".format(self.server["url"], self.endpoint, args_in_query)
        return None

    def get_request_params_query(self, parameters=None):
        """
        Generate the string of parameters for a get request
        :param parameters: dict of parameters (parameter_name, parameter_value)
        :return: String containing the parameters for the get request
        """
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
        """
        Build the parameter string for one parameter
        :param parameters: dict of parameters (parameter_name, parameter_value)
        :param parameter: selected parameter name
        :return:
        """
        # Build single param string
        try:
            ApiRequest.extract_parameter(parameters, parameter)
            return "{}={}".format(parameter["name"], parameters[parameter["name"]])
        except (RequestException.MissingRequiredParameterException, RequestException.IgnoredParameterException) as e:
            raise RequestException.RequestAbortedException(str(e))

    @staticmethod
    def extract_parameter(parameters, parameter):
        """
        Handle the given parameter
        :param parameters: dict of parameters (parameter_name, parameter_value)
        :param parameter: selected parameter name
        :return: {parameter_name: parameter_value} if parameter found,
            exception raised if required parameter is missing (MissingRequiredParameterException)
            or if
        """
        if "required" in parameter and parameter["required"] and parameter["name"] not in parameters:
            raise RequestException.MissingRequiredParameterException(
                "Required parameter '{}' is missing!".format(parameter["name"]))
        elif parameter["name"] not in parameters:
            # TODO: check if additional parameter is given (not in OpenApi Specs)
            raise RequestException.IgnoredParameterException("Parameter '{}' is ignored!".format(parameter["name"]))
        else:
            return {parameter["name"]: parameters[parameter["name"]]}

    def check_response(self, status_code):
        """
        Check if a response is defined for the given status_code
        :param status_code: value of the status_code to check
        :return: Raise OpenApiDefinitionException.StatusCodeException if missing
        """
        if status_code not in self.endpoint_definition["responses"]:
            raise OpenApiDefinitionException.StatusCodeException(
                "Status code {}:{}:{} is missing.".format(self.endpoint, self.request_type, status_code))
        return True

    def process_response(self, url, response, error_flag):
        """
        Create std response
        :param url: url of the request
        :param response: response of the api call
        :param error_flag: if True -> Gateway connection error
        :return: std response
        """
        # Process response
        api_response = ApiResponse(url, response, error_flag=error_flag)
        output = api_response.to_object()
        # Generate schema
        try:
            if self.check_response(str(response.status_code)):
                schema = self.__get_response_schema(str(response.status_code), "application/json")
                schema["components"] = {"schemas": {}}
                if self.components is not None and "schemas" in self.components:
                    schema["components"]["schemas"] = self.components["schemas"]
                # Validate against schema
                if not JsonHandler.validate(output["response"]["Payload"], schema, "response")[0]:
                    output["response"]["Message"] = "WARNING: {}".format(
                        "Response doesn't correspond to predefined schema!"
                    )
            else:
                output["response"]["Payload"] = response.json()
        except OpenApiDefinitionException.StatusCodeException:
            print("No schema found for validation of status_code {}!".format(response.status_code))
        return output

    def __get_response_schema(self, status_code, result_type):
        """
        Extract schema of the OpenApi Specs for the given status_code and result_type
        :param status_code: status_code to search for (ex.: "get")
        :param result_type: result_type to search for (ex.: "application/json")
        :return: schema as json object
        """
        output = None
        if "responses" in self.endpoint_definition and status_code in self.endpoint_definition["responses"]:
            if "content" in self.endpoint_definition["responses"][status_code] \
                    and result_type in self.endpoint_definition["responses"][status_code]["content"]:
                output = Openapi2JsonConverter.convert_open_api_specs_to_json_schema(
                    self.endpoint_definition["responses"][status_code]["content"][result_type]["schema"]
                )
            else:
                print("Response type {} undefined!".format(result_type))
        else:
            print("Status code {} undefined!".format(status_code))
        return output

    def call(self, url, body=None):
        """
        Process the API call
        :param url: url to call
        :param body: body to send
        :return: std response
        """
        # Empty because this is only the interface definition
        pass


class ApiPostRequest(ApiRequest):
    """
    Post handler
    """

    def call(self, url, body=None):
        if url is not None:
            try:
                response = requests.post(url=url, json=body, auth=self.authentication.authentication_func)
                error_flag = False
            except (requests.exceptions.InvalidURL, requests.exceptions.ConnectionError):
                # TODO: Adjust response for Exception handling
                response = MockResponse({}, 500)
                error_flag = True
        else:
            response = None
            error_flag = True
        return self.process_response(url, response, error_flag)


class ApiGetRequest(ApiRequest):
    """
    Get handler
    """

    def call(self, url, body=None):
        if url is not None:
            try:
                response = requests.get(url=url, auth=self.authentication.authentication_func)
                error_flag = False
            except (requests.exceptions.InvalidURL, requests.exceptions.ConnectionError):
                # TODO: Adjust response for Exception handling
                response = MockResponse({}, 500)
                error_flag = True
        else:
            response = None
            error_flag = True
        return self.process_response(url, response, error_flag)


class ApiPutRequest(ApiRequest):
    """
    Put handler
    """

    def call(self, url, body=None):
        # TODO: implement for PUT request
        pass


class ApiDeleteRequest(ApiRequest):
    """
    Delete handler
    """

    def call(self, url, body=None):
        # TODO: implement for DELETE request
        pass
