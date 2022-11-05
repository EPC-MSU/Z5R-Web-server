#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import time
import random


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

    def _generate_id(self):
        return random.randint(0, 2^32 - 1)

    def get_messages(self):
        ret = self.out_pending.copy()
        self.out_pending.clear()
        return ret

    def success(self, req_id):
        # print('ANSWER TO %d FROM CONTROLLER %d' % (req_id, sn))
        # считаем команду успешно отправленной и удалаем из базы
        # cursor.execute('DELETE FROM tasks WHERE id = %d' % req_id)
        # sql_conn.commit()
        pass

    def power_on_handler(self, msg_json, req_id):
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

    def ping_handler(self, msg_json, req_id):
        active = msg_json.get('active')
        mode = msg_json.get('mode')
        cursor.execute("""
                                        UPDATE controllers
                                        SET mode = %d,last_conn = %d
                                        WHERE serial = %d AND type = '%s'
                                           """ % (mode, int(time.time()), sn, device_type))
        sql_conn.commit()
        # прверка флага active в базе. Если не совпадает с присланным контроллером - запрос на изменение active
        if active != ctrl.get('active'):
            answer.append(json.loads('{"id":0,"operation":"set_active","active": %d}' % ctrl.get('active')))

    def check_access_handler(self, msg_json, req_id):
        card = msg_json.get('card')
        reader = msg_json.get('reader')
        print('CHECK ACCESS FROM CONTROLLER %d [%s on %d]' % (sn, card, reader))

        # Для примера будем всех пропускать
        granted = 1
        answer.append(json.loads('{"id":%d,"operation":"check_access","granted":%d}' % (req_id, granted)))

    def events_handler(self, events_json, req_id):
        for event in events_json:
            ev_time = int(time.mktime(
                datetime.datetime.strptime(event.get('time'), '%Y-%m-%d %H:%M:%S').timetuple()
            ))

        answer.append(json.loads('{"id":%d,"operation":"events","events_success":%d}' % (req_id, event_cnt)))
        cursor.execute("""
                       INSERT INTO events (time,event,flags,card)
                       VALUES (%d, %d ,%d, '%s')
                       """ % (ev_time, event.get('event'), event.get('flag'), event.get('card')))

    def get_interval(self):
        return self.interval

    def open_door(self):

        # cursor.execute("""
        #                INSERT INTO tasks (serial,type,json)
        #                VALUES (40646, 'Z5RWEB', '{"operation":"open_door","direction": 0}')
        #                """)
        pass

    def add_card(self):
        # conn = sqlite3.connect('service_data/example.sqlite')
        # cursor = conn.cursor()
        # cursor.execute("""
        #                INSERT INTO tasks (serial,type,json)
        #                VALUES (40646, 'Z5RWEB',
        #                       '{"operation":"add_cards","cards":[{"card": "A8C19E002900","flags": 0,"tz": 255}]}')
        #                """)
        # conn.commit()
        # conn.close()
        pass

    def del_card(self):
        # conn = sqlite3.connect('service_data/example.sqlite')
        # cursor = conn.cursor()
        # cursor.execute("""
        #                INSERT INTO tasks (serial,type,json)
        #                VALUES (40646, 'Z5RWEB',
        #                       '{"operation":"del_cards","cards":[{"card": "A8C19E002900"}]}')
        #                """)
        # conn.commit()
        # conn.close()
        pass

    def set_tz(self):
        # conn = sqlite3.connect('service_data/example.sqlite')
        # cursor = conn.cursor()
        # cursor.execute("""
        #                INSERT INTO tasks (serial,type,json)
        #                VALUES (40646, 'Z5RWEB',
        #                       '{"operation":"set_timezone","zone":0,"begin":"00:00","end":"23:59","days":"01111111"}')
        #                """)
        # conn.commit()
        # conn.close()
        pass

    def set_door(self):
        # conn = sqlite3.connect('service_data/example.sqlite')
        # cursor = conn.cursor()
        # cursor.execute("""
        #                INSERT INTO tasks (serial,type,json)
        #                VALUES (40646, 'Z5RWEB',
        #                       '{"operation":"set_door_params","open": 10,"open_control":10,"close_control": 10}')
        #                """)
        # conn.commit()
        # conn.close()
        pass
