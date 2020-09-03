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
    Read/write the metadata
    """

    @staticmethod
    def read_json(filename):
        """
        Import the json file
        :param filename:
        :return:
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
        """ Export the json object to a json file """
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
        :param json_object:
        :param json_schema:
        :param validation_type: [None, "api_definition", "body", "response"]
        :return:
        """
        try:
            try:
                jsonschema.validate(json_object, json_schema)
                return True
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
                print("SchemaError: {}".format(e))
                return False
        except (ApiDefinitionValidationException, BodyValidationException, ResponseValidationException) as e:
            print(e.message)
            return False
