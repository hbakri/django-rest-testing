import unittest

from rest_testing import APIViewTestScenario


class APIViewTestScenarioTest(unittest.TestCase):
    def test_str(self):
        scenario = APIViewTestScenario(
            description="Test scenario",
            path_parameters={"id": 1},
            query_parameters={"q": "test"},
            request_body={"name": "Test"},
            request_headers={"X-Test-Header": "test-value"},
            expected_response_status=200,
            expected_response_body_type=dict,
            expected_response_body={"id": 1, "name": "Test"},
        )
        expected_str = (
            "APIViewTestScenario:\n"
            "\tdescription=Test scenario\n"
            "\tpath_parameters={'id': 1}\n"
            "\tquery_parameters={'q': 'test'}\n"
            "\trequest_body={'name': 'Test'}\n"
            "\trequest_headers={'X-Test-Header': 'test-value'}\n"
            "\texpected_response_status=200\n"
            "\texpected_response_body_type=<class 'dict'>\n"
            "\texpected_response_body={'id': 1, 'name': 'Test'}"
        )
        self.assertEqual(str(scenario), expected_str)
