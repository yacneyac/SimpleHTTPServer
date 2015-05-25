#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
"""
Propose: 
Author: 'yac'
Date: 
"""

import json
from BaseHTTPServer import BaseHTTPRequestHandler
from urllib import pathname2url
from urlparse import parse_qs
from os.path import getmtime
from mimetypes import MimeTypes
mime_guess_type = MimeTypes().guess_type

import Cookie
cookie = Cookie.SimpleCookie()


from utils import STATIC_DIR
from view import app_, session

GET_MAP_URL = app_.get_map_url
POST_MAP_URL = app_.post_map_url

log_access = app_.init_logger('[ACCESS]', for_access=True)
log = app_.init_logger('[HANDLER]')


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        """ Implemented GET method """
        if self.path == "/":
            self.path = "/index.html"

        try:
            qs = ''
            if '?' in self.path:
                self.path, qs = self.path.split('?')

            # static
            mimetype = mime_guess_type(pathname2url(self.path))[0]
            if mimetype:



                file_path = STATIC_DIR + self.path
                mod_time = self.date_time_string(getmtime(file_path))


                if self.headers.dict.get('if-modified-since', '') == mod_time:
                    self.send_response(304)
                    self.send_header('Last-Modified', mod_time)
                    self.end_headers()
                    return

                #Open the static file requested and send it
                with open(file_path) as f:
                    self.send_response(200)
                    self.send_header('Content-type', mimetype)
                    self.send_header('Last-Modified', mod_time)
#                    self.send_header('ETag', '"551e6c60-40d8"')
                    self.end_headers()
                    self.wfile.write(f.read())
                return

            for route in GET_MAP_URL:
                matched = route['_regex'].search(self.path)
                if matched:
                    if not 'GET' in route['methods']:
                        return self.send_error(405, 'Method Not Allowed')

                    session_id = self._get_session()

                    if not session_id in session.session:
                        return self.send_response(401)

                    if session.is_expire(session_id):
                        return self.send_response(401, 'expired')

                    self.send_HEAD(session_id)

                    variables = matched.groupdict()
                    if qs:
                        variables.update(parse_qs(qs))

                    log.debug('%s: var %s' % (route['view_func'], variables))
                    self.wfile.write(json.dumps(route['view_func'](**variables)))
                    return

            log.error('Bad request <%s> for GET method.', self.path)
            return self.send_error(400, 'Bad Request')
        except IOError:
            log.error('File Not Found: %s', self.path)
            self.send_error(404, 'File Not Found: %s' % self.path)
        except StandardError:
            log.exception('ERROR in GET\n')
            self.send_error(500, 'Internal Server Error')

    def do_POST(self):
        """ Implemented POST method """
        try:
            for route in POST_MAP_URL:
                matched = route['_regex'].search(self.path)
                if matched:
                    variables = matched.groupdict()

                    if not 'POST' in route['methods']:
                        return self.send_error(405, 'Method Not Allowed')


                    session_id = self._get_session()

                    if 'login' in self.path or 'logout' in self.path:
                        if session_id in session.session:
                            # update exp_date for login and del for logout
                            variables['session_id'] = session_id

                    elif session_id in session.session:

                        if session.is_expire(session_id):
                            self.send_error(401, 'expired')
                            return
                    else:
                        self.send_error(401)
                        return

#                    content_len = int(self.headers['Content-Length'])
#                    if content_len:
                    data = self.rfile.read(int(self.headers['Content-Length']))
                    if data:
                        variables.update(json.loads(data))

                    response = route['view_func'](**variables)

                    self.send_HEAD(session.session_id)
                    session.session_id = None

                    self.wfile.write(json.dumps(response))
                    return

            log.error('Bad request <%s> for POST method.', self.path)
            return self.send_error(400, 'Bad Request')
        except StandardError:
            log.exception('ERROR in POST\n')
            self.send_error(500, 'Internal Server Error')

    def log_message(self, format, *args):
        log_access.info(format, *args)

    def send_HEAD(self, session_id):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        if session_id:
            self.send_header('Set-cookie', 'session_id=%s; Path=/;' % session_id)
#            session.session_id = None
        self.end_headers()

    def _get_session(self):
        cookie.load(self.headers.dict.get('cookie', ''))

        session_id = ''
        if 'session_id' in cookie:
            session_id = cookie['session_id'].value

        return session_id
