import os
import sys

from .ApiAuthentication import ApiAuthentication
from .ApiOperations import ApiOperations
from .JsonHandler import JsonHandler


class ApiConnector:
    """
    Class for connection to the API
    """
    DEBUG = False

    def __init__(self, configuration_file, is_openapi=True, authentication=None, parameters=None):
        """
        API defined by configuration file with given authentication
        :param configuration_file: OpenApiSpecs file with definition of the API
        :param is_openapi: set to False to deactivate the schema validation against OpenApi Specs standard
        :param authentication: authentication info
        :param parameters: parameters to initialize the authentication
        """
        self.configuration_file = configuration_file
        self.is_openapi = is_openapi
        self.authentication = ApiAuthentication(authentication_method=authentication, parameters=parameters)
        self.server = {"url": None, "description": None}
        self.resources = None
        self.paths = {}
        self.__get_resources()

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

    def get_endpoint_definition(self, resource, request_type):
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
