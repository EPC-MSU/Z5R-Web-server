#!/usr/bin/env python
# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
import logging
import z5r
import base64
import os
import sqlite3
from urllib.parse import urlparse, parse_qs


MAXIMUM_POST_LENGTH = 2000
TCP_PORT = 80


z5r_dict = dict()
auth = ''


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self._auth = base64.b64encode(auth.encode()).decode()
        super().__init__(*args, **kwargs)

    def do_HEAD(self):  # noqa
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_AUTHHEAD(self):  # noqa
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Z5R Web control page"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _get_page(self, path, query):
        if path == '/control':
            # Handle an action if any
            z5r.action_handler(query, z5r_dict)
            # Display control page
            return z5r.get_page(z5r_dict)
        elif path == '/' or path == '' or path == '/attendance':
            return z5r.get_attendance_page()
        elif path == '/users':
            # Handle an action if any
            z5r.users_handler(query, z5r_dict)
            # Display control page
            return z5r.get_users_page()
        else:
            raise ValueError('Path not found.')

    def do_GET(self):  # noqa
        if self.headers.get('Authorization') is None:
            self.do_AUTHHEAD()
            self.wfile.write(b'no auth header received')
        elif self.headers.get('Authorization') == 'Basic ' + self._auth:
            # Parse and process parameters in URL
            parsed = urlparse(self.path)
            try:
                answer = self._get_page(parsed.path, parse_qs(parsed.query, keep_blank_values=True))
            except ValueError:
                self.send_error(404, 'Not found')
                self.end_headers()
                return

            self.do_HEAD()
            answer = z5r.inject_top_bar(answer)
            self.wfile.write(answer.encode('utf-8'))
        else:
            self.do_AUTHHEAD()
            self.wfile.write(self.headers.get('Authorization').encode('utf-8'))
            self.wfile.write(b'not authenticated')

    def do_POST(self):  # noqa
        parsed = urlparse(self.path)
        if parsed.path == '/connect':
            # Length must not exceed MAXIMUM_POST_LENGTH
            msg_len = int(self.headers.get('Content-Length'))
            if msg_len > MAXIMUM_POST_LENGTH:
                logging.error(self.headers.get('User-Agent', failobj='User-Agent not found')
                              + ' sent POST request with length more than {}.'.format(MAXIMUM_POST_LENGTH))
                self.send_error(400, 'Bad Request')

            msg = self.rfile.read(msg_len)
            logging.debug('Received: {}'.format(msg))

            # Did we receive a correct JSON
            try:
                jsn = json.loads(msg)
            except ValueError:
                logging.error(self.headers.get('User-Agent', failobj='User-Agent not found') +
                              ' sent POST request that is not a JSON object.')
                self.send_error(400, 'Bad Request')
                return

            sn = int(jsn.get('sn'))
            device_type = jsn.get('type')
            messages = jsn.get('messages')
            logging.debug('A request with serial number {} and device type {}'
                          ' was received with {} messages.'.format(sn, device_type, len(messages)))

            if sn not in z5r_dict:
                z5r_dict[sn] = z5r.Z5RWebController(sn)
                z5r_dict[sn].set_active()

            for msg_json in messages:
                req_id = msg_json.get('id')
                if req_id is None:
                    logging.error('No id in {} from {} sn {}. Skipping message.'.format(msg_json, device_type, sn))
                    continue

                operation = msg_json.get('operation')  # Get operation type for processing
                if operation is None:  # No operation means it is an answer from Z5R
                    if msg_json.get('success') == 1:
                        logging.debug('Success from {} sn {} on request id {}.'.format(device_type, sn, req_id))
                        z5r_dict[sn].success(req_id)
                    else:
                        logging.error('Unknown answer {} from {} sn {}.'.format(msg_json, device_type, sn))

                elif operation == 'power_on':  # Power on operation is sent to make initialization
                    logging.info('Power on from {} sn {} received.'.format(device_type, sn))
                    z5r_dict[sn].power_on_handler(msg_json, req_id)
                    # Response is not required

                elif operation == 'ping':  # Periodical signal to request data from server
                    logging.debug('Ping from {} sn {} received.'.format(device_type, sn))
                    z5r_dict[sn].ping_handler(msg_json, req_id)
                    # Response is a list of messages

                elif operation == 'check_access':  # Pass/block check for online server mode only
                    logging.debug('Check access from {} sn {} received.'.format(device_type, sn))
                    z5r_dict[sn].check_access_handler(msg_json, req_id)
                    # Must respond

                elif operation == 'events':
                    logging.debug('Events from {} sn {} received.'.format(device_type, sn))
                    z5r_dict[sn].events_handler(msg_json.get('events'), req_id)
                    # Must respond

                else:
                    logging.error('Unknown operation {} from {} sn {}'.format(operation, device_type, sn))

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            answer = '{"date":"%s","interval":%d,"messages":%s}' % (
                time.strftime('%Y-%m-%d %H:%M:%S'),
                z5r_dict[sn].get_interval(),
                json.dumps(z5r_dict[sn].get_messages(max_size=1500))
            )
            answer = answer.encode('utf-8')
            logging.debug('Sent: {}'.format(answer))
            self.wfile.write(answer)
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            answer = 'Dummy'
            answer = answer.encode('utf-8')
            self.wfile.write(answer)


def _check_table():
    con = sqlite3.connect('service_data/z5r.db')
    cur = con.cursor()
    cur.execute('SELECT name FROM sqlite_master WHERE "name"="users"')
    if cur.fetchone() is None:
        cur.execute('CREATE TABLE users(card, username)')
        cur.execute('CREATE UNIQUE INDEX card_index ON users (card)')


def run():
    try:
        logging.basicConfig(filename='service_data/z5r.log', level=logging.WARNING)
    except FileNotFoundError as e:
        print(e)
        print('There is no service_data folder in the root of the service folder. '
              'It seems that you are not using docker-compose.yaml configuration. '
              'Docker-compose sets working directory in the root of the repository and '
              'mount a volume for user data in the service_data folder.\n'
              'If you want to run just Dockerfile, you can create service_data folder yourself. '
              'If you want to run outside of a container then run python from the root folder like this:\n'
              'python3 src/httpd.py')
        exit(1)

    # Check and prepare service data folder
    if not os.path.isdir('service_data'):
        os.mkdir('service_data', 0o777)
    # Check and prepare auth file
    if not os.path.isfile('service_data/auth'):
        auth_file = open('service_data/auth', 'w')
        auth_file.write('z5r:im_mellon')
        auth_file.close()

    auth_file = open('service_data/auth', 'r')
    global auth
    auth = auth_file.read()
    auth_file.close()

    _check_table()

    logging.info('http server is starting...')
    server_address = ('0.0.0.0', TCP_PORT)
    httpd = HTTPServer(server_address, HTTPRequestHandler)
    logging.info('http server is running...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
