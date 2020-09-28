import json
import os
import traceback

import jsonschema

from ..exceptions.ValidationException import ApiDefinitionValidationException
from ..exceptions.ValidationException import BodyValidationException
from ..exceptions.ValidationException import ResponseValidationException
from ..exceptions.ValidationException import ValidationException


class JsonHandler:
    """
    Read/write a json file
    """

    @staticmethod
    def read_json(filename):
        """
        Import the json file
        :param filename: path of the file
        :return: Python object
        """
        try:
            with open(filename, 'r') as json_file:
                resources = json.load(json_file)
            return resources
        except FileNotFoundError:
            print("File {} not found!".format(filename))
            print("File in ./:")
            for file in os.scandir("."):
                print(file.name)
            return {}

    @staticmethod
    def write_json(filename, json_object, overwrite=False):
        """
        Export the json object to a json file
        :param filename: path of the file
        :param json_object: Python object
        :param overwrite: if True, overwrite
        :return: True if the writing process ended successfully
        """
        try:
            saved_content = JsonHandler.read_json(filename)
            if overwrite or (saved_content == {}):
                with open(filename, 'w') as fp:
                    fp.write(str(json.dumps(json_object)))
                return True
            else:
                return False
        except IOError:
            traceback.print_stack()
            print(json_object)
            print("Something went wrong!")
            return False

    @staticmethod
    def validate(json_object, json_schema, validation_type=None):
        """
        Validate jsonObject against jsonSchema
        :param json_object: json object to check
        :param json_schema: json schema to use for the validation
        :param validation_type: [None, "api_definition", "body", "response"]
        :return: (True/False, error_message)
        """
        try:
            try:
                jsonschema.validate(json_object, json_schema)
                return True, ""
            except jsonschema.exceptions.ValidationError as e:
                message = "ValidationError - {}: {}".format(validation_type, e.message)
                if validation_type == "api_definition":
                    raise ApiDefinitionValidationException(message)
                elif validation_type == "body":
                    raise BodyValidationException(message)
                elif validation_type == "response":
                    raise ResponseValidationException(message)
                else:
                    raise ValidationException(message)
            except jsonschema.exceptions.SchemaError as e:
                return False, "SchemaError: {}".format(e)
        except ValidationException as e:
            return False, str(e)
