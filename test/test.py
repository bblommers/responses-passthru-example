import unittest
import requests
import responses
from moto import mock_dynamodb
from moto.core.models import responses_mock
import boto3


def my_function():
    # Mock this website
    requests.post("https://example.org")

    # Passthrough this website
    assert requests.get("http://ip.jsontest.com").status_code == 200

    return "OK"


def create_instance_and_send_email():
    ddb = boto3.client("dynamodb", "us-east-1")
    assert ddb.list_tables()["TableNames"] == []
    my_function()
    return "OK"


@mock_dynamodb
class MyTest(unittest.TestCase):
    def setUp(self):
        self.r_mock = responses.RequestsMock(assert_all_requests_are_fired=True)
        responses_mock._real_send = self.r_mock.unbound_on_send()
        self.r_mock.start()
        self.r_mock.add_passthru("http://ip.jsontest.com")

    def tearDown(self):
        self.r_mock.stop()
        self.r_mock.reset()

    def test_indexing(self):
        self.r_mock.add(responses.POST, "https://example.org", status=200)
        self.assertEqual("OK", my_function())

    def test_create_instance(self):
        self.r_mock.add(responses.POST, "https://example.org", status=200)
        self.assertEqual("OK", create_instance_and_send_email())
