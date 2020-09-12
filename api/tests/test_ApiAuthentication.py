import os
import requests
from api.exceptions.AuthenticationException import AuthenticationException
from api.model.ApiAuthentication import ApiAuthentication


def test_constructor_undefined_authentication():
    """
    Test ApiAuthentication with undefined authentication
    """
    try:
        ApiAuthentication(authentication_method="unknown")
        is_unknown = False
        err_message = ""
    except AuthenticationException as e:
        is_unknown = True
        err_message = str(e)
    assert is_unknown
    assert err_message == "unknown is not implemented."


def test_constructor_authentication_no_auth():
    """
    Test ApiAuthentication without auth
    """
    try:
        api = ApiAuthentication()
        authentication_check = True
    except AuthenticationException as e:
        authentication_check = False
    assert authentication_check
    assert api.authentication is None


def test_constructor_authentication_basic_auth_missing_parameters():
    """
    Test ApiAuthentication with BasicAuth authentication
    """
    try:
        ApiAuthentication(authentication_method="HTTPBasicAuth")
        missing_parameters = False
        err_message = ""
    except AuthenticationException as e:
        missing_parameters = True
        err_message = str(e)
    assert missing_parameters
    assert err_message == "Parameter keys (username, password) are missing."


def test_constructor_authentication_basic_auth_missing_environ_variables():
    """
    Test ApiAuthentication with BasicAuth authentication
    """
    try:
        my_parameters = {"username": "my_user", "password": "my_pass"}
        ApiAuthentication(authentication_method="HTTPBasicAuth", parameters=my_parameters)
        missing_parameters = False
        err_message = ""
    except AuthenticationException as e:
        missing_parameters = True
        err_message = str(e)
    assert missing_parameters
    assert err_message == "Parameter values (my_user, my_pass) are missing."


def test_constructor_authentication_basic_auth_all_environ_variables():
    """
    Test ApiAuthentication with BasicAuth authentication
    """
    try:
        my_parameters = {"username": "my_user", "password": "my_pass"}
        os.environ["my_user"] = "user"
        os.environ["my_pass"] = "pass"
        api = ApiAuthentication(authentication_method="HTTPBasicAuth", parameters=my_parameters)
        authentication_check = True
    except AuthenticationException as e:
        authentication_check = False
    assert authentication_check
    assert isinstance(api.authentication, requests.auth.HTTPBasicAuth)
