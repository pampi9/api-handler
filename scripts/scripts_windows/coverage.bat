cd ../../api
coverage run -m pytest^
 tests\test_ApiConnector.py^
 tests\test_ApiOperations.py^
 tests\test_JsonHandler.py^
 && coverage html
cd ../scripts/scripts_windows

