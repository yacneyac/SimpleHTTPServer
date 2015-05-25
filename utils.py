#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

"""
Propose: 
Author: 'yac'
Date: 
"""
import os
import ConfigParser

CONF_FILE = 'conf/web.conf'
STATIC_DIR = 'static'
LOG_PATH = '/var/log/web_console.log'

SYS_ERROR = {'success': False, 'errorMessage': 'server_error'}


def get_configuration(config_file=CONF_FILE):
    """ Get parameters from configuration file """
    cfg = {}
    try:
        if config_file.startswith("."):
            config_file = os.path.join(os.path.realpath(os.path.dirname(__file__)), config_file)
        if not os.path.isfile(config_file):
            raise RuntimeError("File '%s' does not exists" % config_file)

        conf_parser = ConfigParser.ConfigParser()
        conf_parser.read(config_file)
        for section in conf_parser.sections():
            sc_cfg = {}
            for item in conf_parser.options(section):
                sc_cfg.update({item: conf_parser.get(section, item)})
            cfg.update({section: sc_cfg})

        return cfg
    except IOError, err:
        message = "Can't read configuration file <%s>: \n%s" % (config_file, err)
        raise IOError(message)
    except Exception:
        raise