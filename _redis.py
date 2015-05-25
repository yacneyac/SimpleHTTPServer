#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
"""
Propose: Describe API for redis DB
Author: 'yac'
Date: 
"""


from redis import Redis


class RedisAPI():

    def __init__(self):
        self.rdb = Redis()

    def set(self, session_id, session_value):
        self.rdb.set(session_id, session_value)

    def get(self, session_id):
        return self.rdb.get(session_id)

    def delete(self, session_id):
        self.rdb.delete(session_id)

