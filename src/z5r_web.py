#!/usr/bin/env python
# -*- coding: utf-8 -*-
import queue


class Z5RWebController:
    def __init__(self, sn):
        self.sn = sn
        self.out_queue = queue.Queue()

    def open(self):

        cursor.execute("""
                       INSERT INTO tasks (serial,type,json)
                       VALUES (40646, 'Z5RWEB', '{"operation":"open_door","direction": 0}')
                       """)

    def add_card(self):
        conn = sqlite3.connect('service_data/example.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO tasks (serial,type,json)
                       VALUES (40646, 'Z5RWEB', '{"operation":"add_cards","cards":[{"card": "A8C19E002900","flags": 0,"tz": 255}]}')
                       """)
        conn.commit()
        conn.close()

    def del_card(self):
        conn = sqlite3.connect('service_data/example.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO tasks (serial,type,json)
                       VALUES (40646, 'Z5RWEB', '{"operation":"del_cards","cards":[{"card": "A8C19E002900"}]}')
                       """)
        conn.commit()
        conn.close()

    def set_tz(self):
        conn = sqlite3.connect('service_data/example.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO tasks (serial,type,json)
                       VALUES (40646, 'Z5RWEB', '{"operation":"set_timezone","zone": 0,"begin":"00:00","end":"23:59","days":"01111111"}')
                       """)
        conn.commit()
        conn.close()

    def set_door(self):
        conn = sqlite3.connect('service_data/example.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO tasks (serial,type,json)
                       VALUES (40646, 'Z5RWEB', '{"operation":"set_door_params","open": 10,"open_control":10,"close_control": 10}')
                       """)
        conn.commit()
        conn.close()
