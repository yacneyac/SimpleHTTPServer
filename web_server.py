#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
"""
Propose: 
Author: 'yac'
Date: 
"""

import sys, os
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(APP_DIR, 'lib'))

from BaseHTTPServer import HTTPServer
from optparse import OptionParser
from socket import error as SocketError

from daemon import Daemon
from view import app_
from _handler import Handler, log

conf = app_.conf


class SimpleWebServer(HTTPServer, Daemon):
    """ Implemented WEB server """

    def __init__(self):
        try:
            HTTPServer.__init__(self, (conf['global']['server_host'], int(conf['global']['server_port'])), Handler)
        except SocketError, err:
            sys.stderr.write('SocketError: %s\n' % err)
            sys.exit(1)

    def run(self):
        log.debug('Started httpserver on port %s', conf['global']['server_port'])
        self.serve_forever()

#    def stop_server(self):
#        self.stop()
#        self.socket.close()


if __name__ == '__main__':
    web_server = SimpleWebServer()

    if conf['global']['daemon'] == 'True':
        parser = OptionParser()
        parser.add_option('-c', '--cfgfile', dest='cfgFile', default=None,
                      help="path to configuration file, by default conf/web.conf")
        parser.add_option('-p', '--pidfile', dest='pidFile', default=None,
                      help="store the process ID in the given file (absolute path)")
        options = parser.parse_args()[0]

        if not options.pidFile:
            sys.stderr.write('Pid file is missing.\n')
            sys.exit(1)

        conf = app_.conf
        web_server.pid_file = options.pidFile
        web_server.start()

    else:  # for development
        try:
            print 'Started httpserver on port: %s' % conf['global']['server_port']
            web_server.serve_forever()
        except KeyboardInterrupt:
            web_server.socket.close()
            print '^C received, shutting down the web server'
