# api-handler
Python API handling based on a yaml configuration file (OpenAPI Specification 3.0.3).

# Content
- API-server mock
- API-client

# Structure of API connector
## Constructor of the instance:
- Required
  - configuration_file: url of the json containing the OpenApiSpecs of the API
- Optional
  - authentication: choice of the authentication mode against the API (default None)
## Select server instance (`select_server_by_description`):
- Required
  - description: value of the description field
- Return True if selection was successful (`server` variable contains the json object) 
## Create authentication object (`create_authentication`):
- Required
  - username (string)
  - password (string)
## Run a request (`run_request`):
- Required
  - resource: endpoint path
  - request_type: type of the request (get, post, ...)
  - parameters: array of key/value
- Optional
  - payload: json input for payload

# Sample
```python
import os

from api.model.ApiConnector import ApiConnector

if __name__ == '__main__':
    # Create API connector
    api = ApiConnector("/path/to/open_api_specs.json", "HTTPBasicAuth")
    # Set authentication
    os.environ["username"] = "my_user_name"
    os.environ["password"] = "my_password"
    my_authentication = api.create_authentication("username", "password")
    # Select server
    api.select_server_by_description("description for server in specs")

    # Generate URL
    my_url = api.get_url("/Sample/Route", "get", {})
    # Run and show request
    print(api.run_request(my_url))
```

# Contributor
François Boissinot ([pampi9](https://github.com/pampi9))

# Maintainer
François Boissinot ([pampi9](https://github.com/pampi9))

# License
Apache License 2.0 (see LICENSE)

