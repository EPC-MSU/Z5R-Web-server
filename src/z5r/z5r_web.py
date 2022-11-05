#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import time
import random
import logging
import json


class Z5RWebController:
    """
    Each controller has a unique serial number. Once created an instance of Z5RWebController keeps Z5R-Web cached state
    and pending state. In response to Z5R-Web request it issues a message to change pending state to an actual state.
    There is a separate transactions list to store pending transactions. Each transaction is sent in response to request
    and resides in list until a successful status is received from Z5R-Web with corresponding id.
    """
    def __init__(self, sn):
        self.sn = sn
        self.online_mode = 0  # Disable online mode for now
        self.interval = 8  # Set fixed interval for now
        self.pending_active = 0  # We start with non active pending state
        self.out_pending = list()  # A list to hold messages to be sent
        self.success_pending = list()  # A list of sent messages ids to be received and verified
        self.fw = None
        self.conn_fw = None
        self.active = None
        self.mode = None

    @staticmethod
    def _generate_id():
        return random.randint(0, 2 ** 31 - 1)

    def get_messages(self, max_size=0):
        if max_size == 0:  # Maximum size unlimited
            ret = self.out_pending.copy()
            self.out_pending.clear()
            return ret
        elif max_size < 2:
            raise ValueError('Can not limit size of message to less than 2 bytes.')
        else:  # Maximum size can be limited by receiving side
            size = 2  # Starting size of list in JSON
            last_index = -1
            for i, msg in enumerate(self.out_pending):
                size += len(json.dumps(msg)) + 1  # Adding JSON separator size and the message
                if size > max_size:
                    break
                last_index = i  # Storing last index
            if last_index == -1:  # No message passed through limit
                return []
            last_index += 1  # Messages passes through the limit and the next one index is what we need for slices
            ret = self.out_pending[:last_index]
            self.out_pending = self.out_pending[last_index:]
            return ret

    def set_active(self):
        self.pending_active = 1

    def success(self, req_id):
        pass

    def power_on_handler(self, msg_json, _):
        # Load controller data and store it
        self.fw = msg_json.get('fw')
        self.conn_fw = msg_json.get('conn_fw')
        self.active = msg_json.get('active')
        self.mode = msg_json.get('mode')
        message = {'id': self._generate_id(),
                   'operation': 'set_active',
                   'active': self.pending_active,
                   'online': self.online_mode
                   }
        self.out_pending.append(message)

    def ping_handler(self, msg_json, _):
        # Update stored controller data
        self.active = msg_json.get('active')
        self.mode = msg_json.get('mode')

    def check_access_handler(self, msg_json, req_id):
        card = msg_json.get('card')
        reader = msg_json.get('reader')
        logging.info('Controller {} has checked access with card {} on reader {}]'.format(self.sn, card, reader))
        message = {'id': self._generate_id(),
                   'operation': 'check_access',
                   'granted': 1
                   }
        self.out_pending.append(message)

    def events_handler(self, events_json, req_id):
        for event in events_json:
            _ = int(time.mktime(
                datetime.datetime.strptime(event.get('time'), '%Y-%m-%d %H:%M:%S').timetuple()
            ))
            card = event.get('card')
            event_type = int(event.get('event'))
            flag = int(event.get('flag'))
            logging.info('Event: sn {} with card {} and event {} flag {}]'.format(self.sn, card, event_type, flag))

        message = {'id': req_id,
                   'operation': 'events',
                   'events_success': len(events_json)
                   }
        self.out_pending.append(message)

    def get_interval(self):
        return self.interval

    def open_door(self, direction):
        message = {'id': self._generate_id(),
                   'operation': 'open_door',
                   'direction': direction
                   }
        self.out_pending.append(message)

    def add_card(self, card):
        message = {'id': self._generate_id(),
                   'operation': 'add_cards',
                   'cards': [
                       {
                           'card': card,
                           'flags': 0,
                           'tz': 255
                       }
                   ]
                   }
        self.out_pending.append(message)

    def del_card(self, card):
        message = {'id': self._generate_id(),
                   'operation': 'del_cards',
                   'cards': [
                       {
                           'card': card
                       }
                   ]
                   }
        self.out_pending.append(message)

    def clear_cards(self):
        message = {'id': self._generate_id(),
                   'operation': 'clear_cards'
                   }
        self.out_pending.append(message)

    def set_tz(self):
        message = {'operation': 'set_timezone',
                   'zone': 0,
                   'begin': '00:00',
                   'end': '23:59',
                   'days': '11111110'
                   }
        self.out_pending.append(message)

    def set_door(self):
        message = {'operation': 'set_door_params',
                   'open': 10,
                   'open_control': 10,
                   'close_control': 10
                   }
        self.out_pending.append(message)
