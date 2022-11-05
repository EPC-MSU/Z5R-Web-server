from unittest import TestCase
from src.z5r import Z5RWebController
import json


class TestZ5RWebController(TestCase):
    def test_creation(self):
        try:
            z5r = Z5RWebController(0)
            z5r.add_card()
            z5r.del_card()
        except Exception:
            self.assertTrue(False)

    def test_power_on_nofail(self):
        try:
            z5r = Z5RWebController(0)
            msg = {'id': 358532290, 'operation': 'power_on', 'fw': '3.42',
                   'conn_fw': '1.0.157', 'active': 0, 'mode': 0,
                   'controller_ip': '172.16.130.233',
                   'reader_protocol': 'wiegand'}
            z5r.power_on_handler(msg, 358532290)
        except Exception:
            self.assertTrue(False)

    def test_power_on_response_format(self):
        try:
            z5r = Z5RWebController(0)
            msg = {'id': 358532290, 'operation': 'power_on', 'fw': '3.42',
                   'conn_fw': '1.0.157', 'active': 0, 'mode': 0,
                   'controller_ip': '172.16.130.233',
                   'reader_protocol': 'wiegand'}
            z5r.power_on_handler(msg, 358532290)
            response = z5r.get_messages()[0]  # First message should be the response
            assert ('id' in response)
            assert ('operation' in response)
            assert ('active' in response)
            assert ('online' in response)
        except Exception:
            self.assertTrue(False)
