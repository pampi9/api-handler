class ApiOperations:
    """
    Class to extract defined parts from the OpenApiSpecs definition json
    """

    def __init__(self, resource, parts=None):
        """
        Extract defined parts out of paths/<endpoint> (resource) in the OpenApiSpecs definition
        :param resource: source to be extracted from
        :param parts: single bloc names to be extracted
        """
        if parts is None:
            parts = ["parameters", "responses", "requestBody"]
        self.operations = {}
        for (method, details) in resource.items():
            self.operations[method] = {}
            for part in parts:
                if part in details:
                    self.operations[method][part] = details[part]
