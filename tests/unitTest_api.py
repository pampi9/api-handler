import unittest
import sys
# https://stackoverflow.com/questions/714063/importing-modules-from-parent-folder/50194143#50194143
from api.model.ComHub import Credentials, ComHub, ComHubFormats, ComHubApi
from api.model.JsonHandler import JsonHandler


class TestAgent(unittest.TestCase):
    def setUp(self):
        Credentials("ShiftBookAdmin")
        self.myComHub = ComHub()
        ComHub.DEBUG = False

    # Unit test : test line format control
    def test_checkOfLineFormat(self):
        line = "0168"
        expected_state = True
        returned_state = ComHubFormats.check_line(line)
        self.assertEqual(expected_state, returned_state)

    # Unit test : test guid format control
    def test_checkOfGuidFormat(self):
        guid = "1806dfe1-c584-bf46-8c0e-5a6cb7f56375"
        expected_state = True
        returned_state = ComHubFormats.check_guid(guid)
        self.assertEqual(expected_state, returned_state)

    # Unit test : test API call 'typGroupsList'
    def test_check_typGroupsList_get(self):
        ComHub.typ_groups_list("0168")
        expected_state = 4
        returned_state = 4
        self.assertEqual(expected_state, returned_state)

    # Unit test : test schema of API.json
    def test_json_configuration(self):
        resources = ComHubApi.__get_resources()
        schema = ComHubApi.get_schema_resources()
        self.assertTrue(JsonHandler.validate(resources, schema), "API.json not valid against schema!")


if __name__ == '__main__':
    main = TestAgent()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAgent)
    unittest.TextTestRunner(verbosity=4, stream=sys.stderr).run(suite)
