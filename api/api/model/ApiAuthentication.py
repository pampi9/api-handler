import os

import requests
from requests.auth import HTTPBasicAuth

from ..exceptions.AuthenticationException import AuthenticationException


class ApiAuthentication:
    """
    Class for the handling of the authentication
    """
    # TODO: implement OAuth2.0
    AUTHENTICATIONS = ["HTTPBasicAuth", None]
    AUTHENTICATIONS_PARAMETERS = {
        "HTTPBasicAuth": ["username", "password"]
    }

    def __init__(self, authentication_method=None, parameters=None):
        """
        ApiAuthentication constructor
        :param authentication_method: method to use (listed in ApiAuthentication.AUTHENTICATIONS)
        :param parameters: dictionary
            with key from the array ApiAuthentication.AUTHENTICATIONS_PARAMETERS[authentication_method]
            and value the key of the os.environ, where the data are put in
        """
        if parameters is None:
            parameters = {}
        self.authentication = None
        if authentication_method in ApiAuthentication.AUTHENTICATIONS:
            self.authentication_method = authentication_method
            if self.__check_parameters(parameters):
                self.__create_authentication(parameters)
        else:
            print("Only {} are available.".format(ApiAuthentication.AUTHENTICATIONS))
            raise AuthenticationException("{} is not implemented.".format(authentication_method))

    def __check_parameters(self, parameters):
        """
        Check the needed parameters based on the mapping defined in parameters
        :param parameters: {authentication key: environment value}
        :return: True if all needed variables have a value in os.environ
        """
        check = True
        if self.authentication_method is not None:
            missing_key = []
            missing_value = []
            for key in ApiAuthentication.AUTHENTICATIONS_PARAMETERS[self.authentication_method]:
                if key in parameters:
                    if parameters[key] not in os.environ:
                        missing_value.append(parameters[key])
                        check = False
                else:
                    missing_key.append(key)
                    check = False
            if len(missing_key) > 0:
                raise AuthenticationException("Parameter keys ({}) are missing.".format(", ".join(missing_key)))
            if len(missing_value) > 0:
                raise AuthenticationException("Parameter values ({}) are missing.".format(", ".join(missing_value)))
        return check

    def __create_authentication(self, parameters):
        """
        Create the authentication for the requests
        :param parameters: parameters for authentication
        """
        self.authentication = None
        if self.authentication_method == "HTTPBasicAuth":
            self.__create_authentication_basic_auth(parameters)

    def __create_authentication_basic_auth(self, parameters):
        """
        Create the authentication for the requests (implementation of HTTPBasicAuth)
        :param parameters: parameters for authentication
        """
        self.authentication = requests.auth.HTTPBasicAuth(
            "{}".format(os.environ[parameters["username"]]),
            os.environ[parameters["password"]]
        )
