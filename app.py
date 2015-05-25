#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
"""
Propose: 
Author: 'yac'
Date: 
"""

import sys
import os
import re
import logging.handlers

from utils import LOG_PATH, get_configuration

RULE_RE = re.compile(r'''
    (?P<static>[^<]*)                           # static rule data
    <
    (?P<variable>[a-zA-Z_][a-zA-Z0-9_]*)        # variable name
    >
''', re.VERBOSE)


class Application():
    def __init__(self):
        self.view_functions = {}
        self.map_url_list = []
        self.get_map_url = []
        self.post_map_url = []
        self.conf = get_configuration()
        self.log = self.init_logger('[APP]')

    def add_url_rule(self, rule, view_func, **options):
        """Connects a URL rule.
        @param rule: request url
        @param view_func: function from view ^)
        @param options: methods
        """
        methods = options.pop('methods', None)

        if methods is None:
            methods = ('GET',)  # add default method

        methods = set(methods)

#        if not 'POST' or not 'GET' in methods:
#            sys.stderr.write('Method <%s> not implemented for function: <%s>.\n' % (methods, view_func.__name__))
#            sys.exit(1)

        map_url = {'rule': rule,
                   'endpoint': view_func.__name__,
                   'view_func': view_func,
                   'methods': methods,
                   '_regex': compile(rule)}

        if 'POST' in methods:
            self.post_map_url.append(map_url)
        elif 'GET' in methods:
            self.get_map_url.append(map_url)

#        self.map_url_list.append(map_url)

    def route(self, rule, **options):
        """A decorator that is used to register a view function for a
        given URL rule.
        @param rule: '/simple/url' or with variable '/simple/url/<some_id>'
        @param options: it's list of methods like methods=['GET', 'POST']
        """
        def decorator(f):
            self.add_url_rule(rule, f, **options)
            return f
        return decorator

    def init_logger(self, log_name='', for_access=None):
        """ Initial logging
         @param log_name: Log name
        """

        backup_count = self.conf['global']['log_count']
        log_lvl = self.conf['global']['log_level']
        access_file = self.conf['global']['log_file_access']
        error_file = self.conf['global'].get('log_file_error')

#        if not error_file:
#            if os.environ.get('XNET_HOME', ''):
#                error_file = '%s%s' % (os.environ['XNET_HOME'], LOG_PATH)
#            else:
#                sys.stderr.write('ERROR: Log file is not configured or XNET_HOME is missing in environment!')
#                sys.exit(2)

        logger = logging.getLogger(log_name)

        if self.conf['global']['daemon'] == 'True':
            if for_access:
                hdlr = logging.handlers.TimedRotatingFileHandler(access_file, when="midnight", backupCount=backup_count)
            else:
                hdlr = logging.handlers.TimedRotatingFileHandler(error_file, when="midnight", backupCount=backup_count)
        else:
            #  logging on screen for dev
            hdlr = logging.StreamHandler()

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)


        logger.setLevel(logging._levelNames[log_lvl])
        logger.propagate = True

        return logger


def parse_rule(rule):
    """Parse a rule and return it as generator.
    If the converter is `None` it's a static url part, otherwise it's a dynamic one.
    """
    pos = 0
    end = len(rule)
    do_match = RULE_RE.match
    used_names = set()
    while pos < end:
        converter = do_match(rule, pos)

        if converter is None:
            yield rule, None  # return simple url without variables
            break
        else:
            data = converter.groupdict()
            variable = data['variable']
            if variable in used_names:
                raise ValueError('variable name %r used twice.' % variable)
            used_names.add(variable)
            yield data['static'], data['variable']
            pos = converter.end()

def compile(domain_rule):
    """Compiles the regular expression and stores it."""

    regex_parts = []

    def _build_regex(rule):
        for p_rule, p_var in parse_rule(rule):
            if p_rule:
                regex_parts.append(re.escape(p_rule))
            if p_var:
                regex_parts.append('(?P<%s>[^/]{1,})' % p_var)

    _build_regex(domain_rule)

    regex = r'^%s$' % (u''.join(regex_parts))
    _regex = re.compile(regex, re.UNICODE)
    print regex
    return _regex