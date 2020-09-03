import os

from api.model.JsonHandler import JsonHandler

RESOURCES = {
    "existing": "tests/resources/Api.json",
    "missing": "tests/resources/missing_Api.json",
    "write_test": "tests/resources/write_test.json",
    "content_json": "tests/resources/content.json",
    "schema_json": "tests/resources/schema.json"
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
    Test JsonHandler.read_json with missing file
    """
    json_content = JsonHandler.read_json(RESOURCES["existing"])
    JsonHandler.write_json(RESOURCES["write_test"], json_content)
    json_content2 = JsonHandler.read_json(RESOURCES["write_test"])
    remove_resource(RESOURCES["write_test"])
    assert json_content == json_content2


def test_validate_json():
    """
    Test JsonHandler.validate
    """
    json_content = JsonHandler.read_json(RESOURCES["content_json"])
    json_schema = JsonHandler.read_json(RESOURCES["schema_json"])
    assert JsonHandler.validate(json_content, json_schema)
