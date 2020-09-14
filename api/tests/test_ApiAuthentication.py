import os
import requests
from api.exceptions.AuthenticationException import AuthenticationException
from api.model.ApiAuthentication import ApiAuthentication


def test_constructor_undefined_authentication():
    """
    Test ApiAuthentication with undefined authentication
    """
    is_unknown = False
    err_message = ""
    try:
        ApiAuthentication(authentication_method="unknown")
    except AuthenticationException as e:
        is_unknown = True
        err_message = str(e)
    assert is_unknown
    assert err_message == "unknown is not implemented."


def test_constructor_authentication_no_auth():
    """
    Test ApiAuthentication without auth
    """
    authentication_check = False
    try:
        ApiAuthentication()
        authentication_check = True
    finally:
        assert authentication_check


def test_constructor_authentication_basic_auth_missing_parameters():
    """
    Test ApiAuthentication with BasicAuth authentication
    """
    missing_parameters = False
    err_message = ""
    try:
        ApiAuthentication(authentication_method="HTTPBasicAuth")
    except AuthenticationException as e:
        missing_parameters = True
        err_message = str(e)
    assert missing_parameters
    assert err_message == "Parameter keys (username, password) are missing."


def test_constructor_authentication_basic_auth_missing_environ_variables():
    """
    Test ApiAuthentication with BasicAuth authentication
    """
    missing_parameters = False
    err_message = ""
    try:
        my_parameters = {"username": "my_user", "password": "my_pass"}
        ApiAuthentication(authentication_method="HTTPBasicAuth", parameters=my_parameters)
    except AuthenticationException as e:
        missing_parameters = True
        err_message = str(e)
    assert missing_parameters
    assert err_message == "Parameter values (my_user, my_pass) are missing."


def test_constructor_authentication_basic_auth_all_environ_variables():
    """
    Test ApiAuthentication with BasicAuth authentication
    """
    my_parameters = {"username": "my_user", "password": "my_pass"}
    os.environ["my_user"] = "user"
    os.environ["my_pass"] = "pass"
    authentication_check = False
    try:
        api = ApiAuthentication(authentication_method="HTTPBasicAuth", parameters=my_parameters)
        authentication_check = True
        assert isinstance(api.authentication, requests.auth.HTTPBasicAuth)
    finally:
        assert authentication_check
