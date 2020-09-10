import os
import sys

import requests

from .ApiOperations import ApiOperations
from .ApiResponse import ApiResponse
from .ApiResponse import MockResponse
from .JsonHandler import JsonHandler


class ApiConnector:
    """
    Class for connection to the API
    """
    AUTHENTICATIONS = ["HTTPBasicAuth", ""]
    DEBUG = False
    UNIT_TEST = False
    UNIT_TEST_WARNING = "Method only valid with UNIT_TEST set to True"

    def __init__(self, configuration_file, is_openapi=True, authentication=""):
        """
        API defined by configuration file with given authentication
        :param configuration_file: OpenApiSpecs file with definition of the API
        :param is_openapi: set to False to deactivate the schema validation against OpenApi Specs standard
        :param authentication: authentication info
        """
        self.configuration_file = configuration_file
        self.is_openapi = is_openapi
        if authentication in ApiConnector.AUTHENTICATIONS:
            self.authentication_method = authentication
            self.authentication = None
        else:
            print("{} is not implemented. Only {} are available.".format(authentication, ApiConnector.AUTHENTICATIONS))
            exit()
        self.server = {"url": None, "description": None}
        self.resources = None
        self.paths = {}
        self.__get_resources()

    def create_authentication(self, username, password):
        """
        Create the authentication for the requests
        :param username: username
        :param password: password
        :return: {-1, 0, 1}
            -1: missing environment variable
            0: no auth
            1: auth and all needed environment variables available
        """
        check = 0
        self.authentication = None
        if self.authentication_method != "":
            failures = []
            for variable in [username, password]:
                if variable not in os.environ:
                    failures.append(variable)
                    check = -1
            if check >= 0:
                if self.authentication_method == "HTTPBasicAuth":
                    self.authentication = requests.auth.HTTPBasicAuth("{}".format(os.environ[username]),
                                                                      os.environ[password])
                    check = 1
            else:
                print("{} variable(s) is not defined in os.environ".format(", ".join(failures)))
        return check

    def select_server_by_description(self, description):
        """
        Select the server by his description out of the lists of available servers
        :param description: description field of the server
        :return: Boolean (true if found)
        """
        self.server = None
        if self.resources is not None and "servers" in self.resources:
            for server in self.resources["servers"]:
                if "description" in server and server["description"] == description:
                    self.server = server
        if self.server is None:
            print("Description {} has not be found!".format(description))
            return False
        return True

    def __get_url(self, resource, request_type, parameters):
        if self.server is not None and "url" in self.server and self.paths is not None:
            endpoint_definition = self.__get_endpoint_definition(resource, request_type)
            if endpoint_definition is not None:
                args = self.__get_request_params_query(endpoint_definition, parameters)
                if args is None:
                    return "{}{}".format(self.server["url"], resource)
                else:
                    return "{}{}?{}".format(self.server["url"], resource, args)
        return None

    @staticmethod
    def process_response(url, response):
        api_response = ApiResponse(url, response)
        return api_response.to_object()

    def run_request(self, resource, request_type, parameters, body=None):
        """ Send a request to the url """
        url = self.__get_url(resource, request_type, parameters)
        if url is not None:
            try:
                if request_type == "get":
                    response = requests.get(url=url, auth=self.authentication)
                else:
                    response = None
                # Generate schema
                schema = self.__get_response_schema_path(
                    self.resources["paths"][resource][request_type], str(response.status_code), "application/json")
                schema["components"] = {}
                schema["components"]["schemas"] = self.resources["components"]["schemas"]
                # Process response
                output = self.process_response(url, response)
                # Validate against schema
                if not JsonHandler.validate(output["response"]["Payload"], schema, "response"):
                    print("Response doesn't correspond to predefined schema! {}".format(output["response"]["Payload"]))
            except (requests.exceptions.InvalidURL, requests.exceptions.ConnectionError) as ex:
                # TODO: Adjust response for Exception handling
                response = MockResponse({}, 500)
                api_response = ApiResponse(url, response, error=True, error_message=str(ex))
                output = api_response.to_object()
            if ApiConnector.DEBUG:
                print(url)
                print(output)
        else:
            output = None
        return output

    def __get_resources(self):
        """
        Import API resources from the configuration file and validate against schema
        :return: None
        """
        self.resources = None
        self.paths = {}
        resources = JsonHandler.read_json(self.configuration_file)
        schema_dir = os.path.abspath(
            os.path.join(os.path.dirname(sys.modules[ApiConnector.__module__].__file__), ".."))
        schema = JsonHandler.read_json("{}/schemas/OAS_schema.json".format(schema_dir))
        if not self.is_openapi or JsonHandler.validate(resources, schema, "api_definition"):
            self.resources = resources
            for (path, resource) in self.resources["paths"].items():
                self.paths[path] = ApiOperations(resource)

    def __get_endpoint_definition(self, resource, request_type):
        if resource in self.paths:
            # endpoint
            if request_type in self.paths[resource].operations:
                # get, post, put, delete
                return self.paths[resource].operations[request_type]
            else:
                print("Request type '{}' not defined".format(request_type))
        else:
            print("Resource '{}' not defined".format(resource))
        return None

    @staticmethod
    def __extract_param(parameters, parameter):
        if "required" in parameter and parameter["required"] and parameter["name"] not in parameters:
            print("Required parameter '{}' is missing".format(parameter))
            return None
        else:
            return {parameter["name"]: parameters[parameter["name"]]}

    @staticmethod
    def __get_formatted_param_in_query(parameters, parameter):
        param = ApiConnector.__extract_param(parameters, parameter)
        if param is not None:
            return "{}={}".format(parameter["name"], parameters[parameter["name"]])
        else:
            return param

    @staticmethod
    def __get_formatted_param_in_path(parameters, parameter):
        return ApiConnector.__extract_param(parameters, parameter)

    @staticmethod
    def __get_request_params_query(endpoint_definition, parameters=None):
        if parameters is None:
            parameters = {}
        args = []
        if "parameters" in endpoint_definition and endpoint_definition["parameters"] is not None:
            for parameter in endpoint_definition["parameters"]:
                # TODO: Handle parameter in header, path
                if parameter["in"] == "query":
                    arg = ApiConnector.__get_formatted_param_in_query(parameters, parameter)
                    if arg is not None:
                        args.append(arg)
        if len(args) == 0:
            return None
        else:
            return "&".join(args)

    @staticmethod
    def __get_response_schema_path(endpoint_definition, response, response_typ):
        if "responses" in endpoint_definition and response in endpoint_definition["responses"]:
            if "content" in endpoint_definition["responses"][response] \
                    and response_typ in endpoint_definition["responses"][response]["content"]:
                return endpoint_definition["responses"][response]["content"][response_typ]["schema"]
            else:
                print("No response type {} defined!".format(response_typ))
        else:
            print("No response {} defined!".format(response))
        return None

    # Methods for unit test only
    def get_endpoint_definition(self, resource, request_type):
        """
        Public access for unit test
        """
        if ApiConnector.UNIT_TEST:
            return self.__get_endpoint_definition(resource, request_type)
        else:
            print(ApiConnector.UNIT_TEST_WARNING)

    def get_url(self, resource, request_type, parameters):
        """
        Public access for unit test
        """
        if ApiConnector.UNIT_TEST:
            return self.__get_url(resource, request_type, parameters)
        else:
            print(ApiConnector.UNIT_TEST_WARNING)

    @staticmethod
    def get_request_params_query(endpoint_definition, parameters=None):
        """
        Public access for unit test
        """
        if ApiConnector.UNIT_TEST:
            return ApiConnector.__get_request_params_query(endpoint_definition, parameters)
        else:
            print(ApiConnector.UNIT_TEST_WARNING)

# "post": {
#   "RequestBody": {
#       "content": "application/json"
#       "schema": {
#           $ref: "#/components/schemas/User"
#       }
#   }
