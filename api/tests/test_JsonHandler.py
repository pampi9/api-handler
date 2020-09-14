import os

from api.model.JsonHandler import JsonHandler

RESOURCES = {
    "existing": "tests/resources/Api.json",
    "missing": "tests/resources/missing_Api.json",
    "write_test": "tests/resources/write_test.json",
    "good_content_json": "tests/resources/content_good.json",
    "bad_content_json": "tests/resources/content_bad.json",
    "good_schema_json": "tests/resources/schema_good.json",
    "bad_schema_json": "tests/resources/schema_bad.json"
}


def remove_resource(filename):
    if os.path.exists(filename) and os.path.isfile(filename):
        os.remove(filename)


def test_missing_json():
    """
    Test JsonHandler.read_json with missing file
    """
    json_content = JsonHandler.read_json(RESOURCES["missing"])
    assert json_content == {}


def test_existing_json():
    """
    Test JsonHandler.read_json with existing file
    """
    json_content = JsonHandler.read_json(RESOURCES["existing"])
    assert json_content != {}


def test_writing_json():
    """
    Test JsonHandler.write_json with missing file
    """
    json_content = JsonHandler.read_json(RESOURCES["existing"])
    JsonHandler.write_json(RESOURCES["write_test"], json_content)
    json_content2 = JsonHandler.read_json(RESOURCES["write_test"])
    remove_resource(RESOURCES["write_test"])
    assert json_content == json_content2


def test_overwriting_json_success():
    """
    Test JsonHandler.write_json with existing file
    """
    json_content = JsonHandler.read_json(RESOURCES["existing"])
    result = JsonHandler.write_json(RESOURCES["existing"], json_content, overwrite=True)
    assert result


def test_overwriting_json_failed():
    """
    Test JsonHandler.write_json with existing file
    """
    json_content = JsonHandler.read_json(RESOURCES["existing"])
    result = JsonHandler.write_json(RESOURCES["existing"], json_content, overwrite=False)
    assert not result


def test_validate_bad_json_schema():
    """
    Test JsonHandler.validate
    """
    json_content = JsonHandler.read_json(RESOURCES["good_content_json"])
    json_schema = JsonHandler.read_json(RESOURCES["bad_schema_json"])
    err_message = [
        "'arra' is not valid under any of the given schemas",
        "",
        "Failed validating 'anyOf' in metaschema['properties']['type']:",
        "    {'anyOf': [{'$ref': '#/definitions/simpleTypes'},",
        "               {'items': {'$ref': '#/definitions/simpleTypes'},",
        "                'minItems': 1,",
        "                'type': 'array',",
        "                'uniqueItems': True}]}",
        "",
        "On schema['type']:",
        "    'arra'"
    ]
    expected_err_message = "SchemaError: {}".format("\n".join(err_message))
    print(JsonHandler.validate(json_content, json_schema)[1])
    assert JsonHandler.validate(json_content, json_schema) == (False, expected_err_message)


def test_validate_good_json():
    """
    Test JsonHandler.validate
    """
    json_content = JsonHandler.read_json(RESOURCES["good_content_json"])
    json_schema = JsonHandler.read_json(RESOURCES["good_schema_json"])
    assert JsonHandler.validate(json_content, json_schema) == (True, "")


def validate_bad_json(validation_type, expected_result):
    json_content = JsonHandler.read_json(RESOURCES["bad_content_json"])
    json_schema = JsonHandler.read_json(RESOURCES["good_schema_json"])
    assert JsonHandler.validate(json_content, json_schema, validation_type) == expected_result


def test_validate_bad_json_none():
    """
    Test JsonHandler.validate
    """
    expected_err_message = "ValidationError - : 'UniqueName' is a required property"
    validate_bad_json("", expected_result=(False, expected_err_message))


def test_validate_bad_json_api_definition():
    """
    Test JsonHandler.validate
    """
    expected_err_message = "ValidationError - api_definition: 'UniqueName' is a required property"
    validate_bad_json("api_definition", expected_result=(False, expected_err_message))


def test_validate_bad_json_body():
    """
    Test JsonHandler.validate
    """
    expected_err_message = "ValidationError - body: 'UniqueName' is a required property"
    validate_bad_json("body", expected_result=(False, expected_err_message))


def test_validate_bad_json_response():
    """
    Test JsonHandler.validate
    """
    expected_err_message = "ValidationError - response: 'UniqueName' is a required property"
    validate_bad_json("response", expected_result=(False, expected_err_message))
