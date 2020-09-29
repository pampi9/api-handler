# api-handler
Python API handling based on a json configuration file (OpenAPI Specification 3.0.3).

# Uses
| Code | License |
| --- | --- |
| [py-openapi-schema-to-json-schema](https://github.com/pglass/py-openapi-schema-to-json-schema) | MIT license |

Install `py-openapi-schema-to-json-schema` w/ `python setup.py build && python setup.py install`

# Content
- API-server mock
- API-client

# Structure of `ApiConnector`
## `__init__`:
Required
  - `str` configuration_file: path of the json containing the OpenApiSpecs of the API

Optional
  - `bool` is_openapi (default: True): The constructor checks the configuration file \
        against the OpenApi Specs schema
  - `str` authentication (default: None): choice of the authentication mode \
        against the API \
        (Actually implemented: "HTTPBasicAuth", None)
  - `dict` parameters (default: None): additional parameters for the authentication \
        (dictionary with \
        the key given by the authentication selected and \
        the value with the os.environ["variable"] you choose to store their value)

## `select_server_by_description`:
Required
  - `str` description: value of the description field \
        (in the servers part, each entry should have an url and a description value)

Return
  - True if selection was successful (`self.server` variable contains the json object) 

# Structure of `ApiRequest`
## `ApiRequest.create_request`:
Required
  - `ApiConnector` api: ApiConnector object
  - `str` endpoint: name of the endpoint
  - `str` method_type: selected method to use for the request

Return
  - a configured ApiRequest object

## `build_url`:
Optional:
  - `dict` parameters (default: None): (key, value) pairs of parameters \
        to include in the url

Return
  - The url string to call

## Run a request (`call`):
url, body=None, authentication=None
Required
  - url: url to call in the api call

Optional
  - `object` body: json input for the body of the request
  - authentication

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
    my_authentication = api.__create_authentication("username", "password")
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

