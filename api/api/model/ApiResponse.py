import os
import sys

from .JsonHandler import JsonHandler


class ApiResponse:
    def __init__(self, url, response, error=False, error_message=""):
        """
        Constructor
        :param url: url of the request
        :param response: requests.Response object
        """
        self.url = url
        self.status_code = response.status_code
        self.content = response.json()
        self.is_empty = (response == "")
        self.is_error = error
        self.error_message = error_message
        schema_dir = os.path.abspath(
            os.path.join(os.path.dirname(sys.modules[ApiResponse.__module__].__file__), ".."))
        self.schema = JsonHandler.read_json("{}/schemas/output.json".format(schema_dir))

    def to_object(self):
        content = {"url": self.url, "status_code": self.status_code,
                   "response": {"StatusCode": 1, "Message": "", "Payload": self.content}
                   }
        if self.is_error:
            content["response"]["StatusCode"] = -1
            content["response"]["Message"] = self.error_message
        elif self.is_empty:
            content["response"]["StatusCode"] = 0
            content["response"]["Message"] = "empty"
        else:
            if isinstance(self.content, list):
                content["response"]["Message"] = "list"
            elif isinstance(self.content, dict):
                content["response"]["Message"] = "dict"
        if not JsonHandler.validate(content, self.schema):
            print("Request std output is not valid against defined schema!")
        return content


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data
