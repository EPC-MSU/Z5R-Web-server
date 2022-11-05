#!/usr/bin/env python
# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
import ssl  # noqa
import logging
import z5r


MAXIMUM_POST_LENGTH = 2000
TCP_PORT = 8080


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.z5r_dict = dict()
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_GET(self):  # noqa
        logging.warning(self.headers.get('User-Agent', failobj='User-Agent not found') +
                        ' sent GET request but GET method is not implemented.')
        self.send_error(501, 'Not Implemented')

    def do_POST(self):  # noqa
        answer = []

        # Length must not exceed 2000
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

        sn = jsn.get('sn')
        device_type = jsn.get('type')
        messages = jsn.get('messages')
        logging.debug('A request with serial number {} and device type {}'
                      ' was received with {} messages.'.format(sn, device_type, len(messages)))

        if sn not in self.z5r_dict:
            self.z5r_dict[sn] = z5r.Z5RWebController(sn)
            self.z5r_dict[sn].set_active()

        for msg_json in messages:
            req_id = msg_json.get('id')
            if req_id is None:
                logging.error('No id in {} from {} sn {}. Skipping message.'.format(msg_json, device_type, sn))
                continue

            operation = msg_json.get('operation')  # Get operation type for processing
            if operation is None:  # No operation means it is an answer from Z5R
                if msg_json.get('success') == 1:
                    logging.debug('Success from {} sn {} on request id {}.'.format(device_type, sn, req_id))
                    self.z5r_dict[sn].success(req_id)
                else:
                    logging.error('Unknown answer {} from {} sn {}.'.format(msg_json, device_type, sn))

            elif operation == 'power_on':  # Power on operation is sent to make initialization
                logging.info('Power on from {} sn {} received.'.format(device_type, sn))
                self.z5r_dict[sn].power_on_handler(msg_json, req_id)
                # Response is not required

            elif operation == 'ping':  # Periodical signal to request data from server
                logging.debug('Ping from {} sn {} received.'.format(device_type, sn))
                self.z5r_dict[sn].ping_handler(msg_json, req_id)
                # Response is a list of messages

            elif operation == 'check_access':  # Pass/block check for online server mode only
                logging.debug('Check access from {} sn {} received.'.format(device_type, sn))
                self.z5r_dict[sn].check_access_handler(msg_json, req_id)
                # Must respond

            elif operation == 'events':
                logging.debug('Events from {} sn {} received.'.format(device_type, sn))
                self.z5r_dict[sn].events_handler(msg_json.get('events'), req_id)
                # Must respond

            else:
                logging.error('Unknown operation {} from {} sn {}'.format(operation, device_type, sn))

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        answer = '{"date":"%s","interval":%d,"messages":%s}' % (
            time.strftime('%Y-%m-%d %H:%M:%S'),
            self.z5r_dict[sn].get_interval(),
            json.dumps(self.z5r_dict[sn].get_messages(max_size=1500))
        )
        logging.debug('Sent: {}'.format(answer))
        self.wfile.write(answer)


def run():
    try:
        logging.basicConfig(filename='service_data/z5r.log', level=logging.DEBUG)
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

    logging.info('http server is starting...')
    server_address = ('0.0.0.0', TCP_PORT)
    httpd = HTTPServer(server_address, HTTPRequestHandler)

#    httpd.socket = ssl.wrap_socket (httpd.socket,
#                                    keyfile="key.pem",
#                                    certfile='cert.pem', server_side=True)

    logging.info('http server is running...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
