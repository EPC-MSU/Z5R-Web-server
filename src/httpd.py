#!/usr/bin/env python
# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sqlite3
import time
import datetime
import ssl
import logging


class Z5RWebController:
    def __init__(self, sn):
        self.sn = sn

    def open(self):
        conn = sqlite3.connect('service_data/example.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO tasks (serial,type,json)
                       VALUES (40646, 'Z5RWEB', '{"operation":"open_door","direction": 0}')
                       """)
        conn.commit()
        conn.close()

    def add_card(self):
        conn = sqlite3.connect('example.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO tasks (serial,type,json)
                       VALUES (40646, 'Z5RWEB', '{"operation":"add_cards","cards":[{"card": "A8C19E002900","flags": 0,"tz": 255}]}')
                       """)
        conn.commit()
        conn.close()

    def del_card(self):
        conn = sqlite3.connect('example.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO tasks (serial,type,json)
                       VALUES (40646, 'Z5RWEB', '{"operation":"del_cards","cards":[{"card": "A8C19E002900"}]}')
                       """)
        conn.commit()
        conn.close()

    def set_tz(self):
        conn = sqlite3.connect('example.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO tasks (serial,type,json)
                       VALUES (40646, 'Z5RWEB', '{"operation":"set_timezone","zone": 0,"begin":"00:00","end":"23:59","days":"01111111"}')
                       """)
        conn.commit()
        conn.close()

    def set_door(self):
        conn = sqlite3.connect('example.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO tasks (serial,type,json)
                       VALUES (40646, 'Z5RWEB', '{"operation":"set_door_params","open": 10,"open_control":10,"close_control": 10}')
                       """)
        conn.commit()
        conn.close()


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_get(self):
        self.send_error(501, 'Not Implemented')

    def power_on_handler(self):
        print('CONTROLLER %d POWER ON' % sn)
        # получим параметры контроллера
        fw = msg_json.get('fw')
        conn_fw = msg_json.get('conn_fw')
        active = msg_json.get('active')
        mode = msg_json.get('mode')
        # если контроллер не найден в базе добавим его
        if ctrl == None:
            print('UNKNOWN CONTROLLER ADD TO BASE')
            cursor.execute("""
                                           INSERT INTO controllers (serial, type, fw, conn_fw, active, mode,last_conn)
                                           VALUES (%d, '%s', '%s' ,'%s', 0, %d, %d)
                                           """ % (sn, type, fw, conn_fw, mode, int(time.time())))
            sql_conn.commit()
            cursor.execute("SELECT * FROM controllers WHERE serial = %d AND type = '%s'" % (sn, type))
            ctrl = cursor.fetchone()
        # если контроллер найден в базе то обновим его параметры
        else:
            cursor.execute("""
                                           UPDATE controllers 
                                           SET fw = '%s',conn_fw = '%s',mode = %d,last_conn = %d  
                                           WHERE serial = %d AND type = '%s'
                                           """ % (fw, conn_fw, mode, int(time.time()), sn, type))
            sql_conn.commit()

        # проверка флага active в базе. Если не совпадает с присланным контроллером - запрос на изменение active
        # также сообщим контроллеру, что сервер поддерживает ONLINE
        if active != ctrl.get('active'):
            answer.append(json.loads('{"id":0,"operation":"set_active","active": %d,"online": 1}' % ctrl.get('active')))

    def do_post(self):
        answer = []

        # Length must not exceed 2000
        msg_len = int(self.headers.getheader('Content-Length'))
        if msg_len > 2000:
            self.send_error(400, 'Bad Request')

        msg = self.rfile.read(msg_len)

        # проверка JSON на валидность
        try:
            jsn = json.loads(msg)
        except ValueError:
            self.send_error(400, 'Bad Request')
            return
        sn = jsn.get('sn')
        type = jsn.get('type')

        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        sql_conn = sqlite3.connect('example.sqlite')
        sql_conn.row_factory = dict_factory
        cursor = sql_conn.cursor()

        # ищем контроллер в базе
        cursor.execute("SELECT * FROM controllers WHERE serial = %d AND type = '%s'" % (sn,type))
        ctrl = cursor.fetchone()

        # получим сообщения контроллера
        msgs_json=jsn['messages']

        for msg_json in msgs_json:
            # получим операцию из сообщения
            operation = msg_json.get('operation')
            req_id = msg_json.get('id')
            # нет операции
            if operation == None:
                # если это ответ на сообщение сервера
                if msg_json.get('success')== 1:
                    print("ANSWER TO %d FROM CONTROLLER %d" % (req_id,sn) )
                    # считаем команду успешно отправленной и удалаем из базы
                    cursor.execute("DELETE FROM tasks WHERE id = %d" % (req_id))
                    sql_conn.commit()
                else:
                    print("UNKNOWN ANSWER:\n%s" % (msg_json) )
            # если это сообщение о включении
            elif operation == 'power_on':


            elif operation == "ping":
                #обновление контроллера в базе
                print("PING FROM CONTROLLER %d" % sn )
                active = msg_json.get('active')
                mode = msg_json.get('mode')
                cursor.execute("""
                                   UPDATE controllers 
                                   SET mode = %d,last_conn = %d  
                                   WHERE serial = %d AND type = '%s'
                                   """ % (mode, int(time.time()),  sn, type))
                sql_conn.commit()
                #прверка флага active в базе. Если не совпадает с присланным контроллером - запрос на изменение active
                if active != ctrl.get('active'):
                    answer.append(json.loads('{"id":0,"operation":"set_active","active": %d}' % ctrl.get('active')))

            elif operation == "check_access":
                #проверка доступа в режиме online
                card = msg_json.get('card')
                reader = msg_json.get('reader')
                print("CHECK ACCESS FROM CONTROLLER %d [%s on %d]" % (sn,card,reader))

                #Для примера будем всех пропускать
                granted = 1
                answer.append(json.loads('{"id":%d,"operation":"check_access","granted":%d}' % (req_id,granted)))



            elif operation == "events":
                #запись событий в базу
                print("EVENTS FROM CONTROLLER %d" % sn )
                events = msg_json.get('events')
                event_cnt = 0;
                for event in events:
                    event_cnt += 1
                    ev_time=int(time.mktime(datetime.datetime.strptime(event.get('time'), "%Y-%m-%d %H:%M:%S").timetuple()))
                    cursor.execute("""
                                   INSERT INTO events (time,event,flags,card)
                                   VALUES (%d, %d ,%d, '%s')
                                   """ % (ev_time, event.get('event'),event.get('flag'),event.get('card')))

                #сообщим контроллеру об успешной записи событий в базу
                sql_conn.commit()
                print("EVENT_SUCCESS: %d" % event_cnt)
                answer.append(json.loads('{"id":%d,"operation":"events","events_success":%d}' % (req_id,event_cnt)))



            else:
                print('UNKNOWN OERATION')

        #поиск задач в базе и формирование посылки контроллеру
        for task_jsn in cursor.execute("SELECT id,json FROM tasks WHERE serial = %d AND type = '%s'" % (sn,type)):
            if (len(json.dumps(answer))+len(task_jsn['json'])) > 1500:
                break
            task = json.loads(task_jsn['json'])
            task['id'] = task_jsn['id']
            answer.append(task)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        answer = '{"date":"%s","interval":%d,"messages":%s}' % (time.strftime("%Y-%m-%d %H:%M:%S"),ctrl.get('interval'),json.dumps(answer))
        self.wfile.write(answer)

        sql_conn.close()

def run():
    logging.basicConfig(filename='service_data/z5r.log', encoding='utf-8', level=logging.DEBUG)
    logging.info('http server is starting...')
    server_address = ('0.0.0.0', 80)
    httpd = HTTPServer(server_address, HTTPRequestHandler)

    httpd.socket = ssl.wrap_socket (httpd.socket,
        keyfile="key.pem",
        certfile='cert.pem', server_side=True)

    logging.info('http server is running...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
