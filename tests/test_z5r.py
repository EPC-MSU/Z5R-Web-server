from unittest import TestCase
from src.z5r import Z5RWebController
from src.z5r.users_page import _get_user_cards_list, _update_users
from src.z5r.common import get_events_by_date
from src.z5r.dbz5r import  DbZ5R
import os
import binascii
from datetime import datetime


os.chdir(os.path.dirname(__file__) + '/..')
if not os.path.isdir('service_data'):
    os.mkdir('service_data', 0o777)


class TestZ5RWebController(TestCase):
    def test_creation(self):
        try:
            Z5RWebController(0)
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

    def test_active_response(self):
        try:
            z5r = Z5RWebController(0)
            z5r.set_active()
            msg = {'id': 358532290, 'operation': 'power_on', 'fw': '3.42',
                   'conn_fw': '1.0.157', 'active': 0, 'mode': 0,
                   'controller_ip': '172.16.130.233',
                   'reader_protocol': 'wiegand'}
            z5r.power_on_handler(msg, 358532290)
            response = z5r.get_messages()[0]  # First message should be the response
            assert (response['active'] == 1)
        except Exception:
            self.assertTrue(False)

    def test_active_toggle(self):
        try:
            z5r = Z5RWebController(0)
            msg = {'id': 358532290, 'operation': 'power_on', 'fw': '3.42',
                   'conn_fw': '1.0.157', 'active': 0, 'mode': 0,
                   'controller_ip': '172.16.130.233',
                   'reader_protocol': 'wiegand'}
            z5r.power_on_handler(msg, 358532290)
            response = z5r.get_messages()[0]  # First message should be the response
            assert (response['active'] == 0)
            msg = {'id': response['id'], 'success': 1}  # Respond that last message was received
            z5r.set_active()  # Toggle active
            z5r.success(msg)  # Report about successful message receiving
            msg = {'id': 89673453, 'operation': 'power_on', 'fw': '3.42',
                   'conn_fw': '1.0.157', 'active': 0, 'mode': 0,
                   'controller_ip': '172.16.130.233',
                   'reader_protocol': 'wiegand'}
            z5r.power_on_handler(msg, 89673453)
            response = z5r.get_messages()[0]  # First message should be the response
            assert (response['active'] == 1)
        except Exception:
            self.assertTrue(False)

    def test_add_delete_card(self):
        try:
            z5r = Z5RWebController(0)
            z5r.set_active()
            msg = {'id': 358532290, 'operation': 'power_on', 'fw': '3.42',
                   'conn_fw': '1.0.157', 'active': 0, 'mode': 0,
                   'controller_ip': '172.16.130.233',
                   'reader_protocol': 'wiegand'}
            z5r.power_on_handler(msg, 358532290)
            z5r.get_messages()  # Clear message queue
            z5r.add_card('00B5009EC1A8', 0, 255)
            response = z5r.get_messages()[0]  # First message should be the response
            assert (response['cards'][0]['card'] == '00B5009EC1A8')
            assert ('flags' in response['cards'][0])
            assert ('tz' in response['cards'][0])
            z5r.del_card('00B5009EC1A8')
            response = z5r.get_messages()[0]  # First message should be the response
            assert (response['cards'][0]['card'] == '00B5009EC1A8')
        except Exception:
            self.assertTrue(False)

    def test_add_many_cards(self):
        try:
            z5r = Z5RWebController(0)
            z5r.set_active()
            msg = {'id': 358532290, 'operation': 'power_on', 'fw': '3.42',
                   'conn_fw': '1.0.157', 'active': 0, 'mode': 0,
                   'controller_ip': '172.16.130.233',
                   'reader_protocol': 'wiegand'}
            z5r.power_on_handler(msg, 358532290)
            z5r.get_messages()  # Clear message queue
            for i in range(0, 25):
                z5r.add_card(binascii.hexlify(os.urandom(6)).decode(), 0, 255)
            total_messages = 0
            while True:
                response = z5r.get_messages(1000)
                total_messages += len(response)
                if len(response) == 0:
                    break
                for msg in response:
                    assert ('card' in msg['cards'][0])
                    assert ('flags' in msg['cards'][0])
                    assert ('tz' in msg['cards'][0])
            # Actually there could be less messages, when multiple cards are added in a single message.
            assert (total_messages == 25)
        except Exception:
            self.assertTrue(False)

    def test_open_door(self):
        try:
            z5r = Z5RWebController(0)
            z5r.set_active()
            msg = {'id': 358532290, 'operation': 'power_on', 'fw': '3.42',
                   'conn_fw': '1.0.157', 'active': 0, 'mode': 0,
                   'controller_ip': '172.16.130.233',
                   'reader_protocol': 'wiegand'}
            z5r.power_on_handler(msg, 358532290)
            z5r.get_messages()  # Clear message queue
            z5r.open_door(0)
            msg = {'id': 1126273268, 'operation': 'ping', 'active': 1, 'mode': 0}
            z5r.ping_handler(msg, 1126273268)
            response = z5r.get_messages()[0]  # First message should be the response
            assert ('id' in response)
            assert (response['operation'] == 'open_door')
            assert ('direction' in response)
        except Exception:
            self.assertTrue(False)

    def test_set_door_params(self):
        try:
            z5r = Z5RWebController(0)
            z5r.set_active()
            msg = {'id': 358532290, 'operation': 'power_on', 'fw': '3.42',
                   'conn_fw': '1.0.157', 'active': 0, 'mode': 0,
                   'controller_ip': '172.16.130.233',
                   'reader_protocol': 'wiegand'}
            z5r.power_on_handler(msg, 358532290)
            z5r.get_messages()  # Clear message queue
            z5r.set_door_params(10, 30, '50')
            msg = {'id': 1126273268, 'operation': 'ping', 'active': 1, 'mode': 0}
            z5r.ping_handler(msg, 1126273268)
            response = z5r.get_messages()[0]  # First message should be the response
            assert ('id' in response)
            assert (response['operation'] == 'set_door_params')
            assert ('open' in response)
            assert ('open_control' in response)
            assert ('close_control' in response)
        except Exception:
            self.assertTrue(False)


class TestUsersPage(TestCase):
    def test_get_all_cards(self):
        try:
            user_cards = _get_user_cards_list()

            for card in   user_cards:
                if card == '000000000000':
                    raise ValueError('One of the cards have no number (000000000000)')
                if len(card) != 12:
                    raise ValueError('One of the cards have length not 12 symbols ({})'.format(card))
        except Exception:
            self.assertTrue(False)

    def test_update_users(self):
        try:
            query = [
                {'name_000000000001': 'test_update_users1'},
                {'name_000000000002': 'test_update_users2'}
                     ]
            _update_users(query)
        except Exception:
            self.assertTrue(False)


class TestCommon(TestCase):
    def test_get_events_by_date(self):
        try:
            dbcon = DbZ5R()
            date = datetime.now()
            dbcon.get_reg_user_card_events_per_day(date)
            dbcon.get_free_reg_cards_events_per_day(date)
            dbcon.get_unregistered_cards_events_per_day(date)

        except Exception:
            self.assertTrue(False)
