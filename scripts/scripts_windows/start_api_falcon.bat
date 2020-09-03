cd ../../api
REM gunicorn is only supported on Windows (statement of 2020.09.01: https://github.com/benoitc/gunicorn/issues/524)
gunicorn api_mock_falcon:api
cd ../scripts/scripts_windows