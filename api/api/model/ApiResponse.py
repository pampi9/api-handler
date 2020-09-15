import os
import sys

from .JsonHandler import JsonHandler


# Response codes: https://tools.ietf.org/html/rfc7231#section-6.3
class ApiResponse:
    """
    Class to handle the response of the API calls
    """

    def __init__(self, url, response, error_flag=False, error_message=""):
        """
        Constructor
        :param url: url of the request
        :param response: requests.Response object
        :param error_flag: if True -> Gateway connection error
        :param error_message: information to put in the std response ("Message" field)
        """
        self.url = url
        self.status_code = response.status_code
        self.content = response.json()
        self.is_empty = (response.json() == "")
        self.is_error = error_flag
        self.error_message = error_message
        schema_dir = os.path.abspath(
            os.path.join(os.path.dirname(sys.modules[ApiResponse.__module__].__file__), ".."))
        self.schema = JsonHandler.read_json("{}/schemas/output.json".format(schema_dir))

    def to_object(self):
        """
        Generate the std response
        :return: std response
        """
        content = {"url": self.url, "status_code": self.status_code,
                   "response": {"StatusCode": 200, "Message": "", "Payload": self.content}
                   }
        if self.is_error:
            content["response"]["StatusCode"] = 504
            content["response"]["Message"] = "Gateway timeout: {}".format(self.error_message)
        elif self.is_empty:
            content["response"]["StatusCode"] = 204
            content["response"]["Message"] = "No content: empty response"
        else:
            if isinstance(self.content, list):
                content["response"]["Message"] = "OK: list"
            elif isinstance(self.content, dict):
                content["response"]["Message"] = "OK: dict"
            else:
                content["response"]["Message"] = "OK"
        if not JsonHandler.validate(content, self.schema):
            print("Request std output is not valid against defined schema!")
        return content


class MockResponse:
    """
    Class to make a mocked response
    """
    def __init__(self, json_data, status_code):
        """
        Create the mock
        :param json_data: response body
        :param status_code: status_code
        """
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        """
        Return the json response
        :return: json_data
        """
        return self.json_data
