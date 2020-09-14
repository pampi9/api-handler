cd ../../api
coverage run -m pytest^
 tests\test_ApiAuthentication.py^
 tests\test_ApiConnector.py^
 tests\test_ApiOperations.py^
 tests\test_ApiRequest.py^
 tests\test_JsonHandler.py^
 && coverage html
cd ../scripts/scripts_unix