#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
"""
Propose: 
Author: 'yac'
Date:

session = {'<session_id>': {'user_id': 'id', 'date_exp': <date exp>}}

"""

import os
import base64
import calendar
from datetime import datetime


class Session():

    def __init__(self):
        self.session_id = None
#        self.rdb = redis.Redis()

        self.is_auth_user = False
        self.session = {}
        self.expire_after = 30  # default in minute

    def generate(self):
        self.session_id = base64.b64encode(os.urandom(32)).strip('==')
        return self.session_id

    def set(self, session_id, user_id):
        if session_id in self.session:
            # update expire date
            self.session[session_id]['date_exp'] = self._timestemp_now() + (self.expire_after * 60)
            return

        self.session[session_id] = {'user_id': user_id,
                                    'date_exp': self._timestemp_now() + (self.expire_after * 60)}

    def get(self, session_id):
        return self.session[session_id]

    def delete(self, session_id):
        if session_id in self.session:
            del self.session[session_id]

    def is_expire(self, session_id):
        if self.session[session_id]['date_exp'] <= self._timestemp_now():
            self.delete(session_id)

            return True

    def _timestemp_now(self):
        return calendar.timegm(datetime.now().utctimetuple())

