class DefinitionException(Exception):
    # Generic
    pass


class RequestTypeException(DefinitionException):
    # Missing request type
    pass


class EndpointException(DefinitionException):
    # Missing endpoint
    pass


class StatusCodeException(DefinitionException):
    # Missing status code
    pass
