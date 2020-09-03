# TODO: add user-defined exceptions for the validation
import jsonschema


class ValidationException(jsonschema.exceptions.ValidationError):
    # Generic
    pass


class BodyValidationException(ValidationException):
    # Specific for Body of request
    pass


class ResponseValidationException(ValidationException):
    # Specific for Response of request
    pass


class ApiDefinitionValidationException(ValidationException):
    # Specific for Api definition of request
    pass
