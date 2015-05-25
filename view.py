#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

"""
Propose: Describe application url
Author: 'yac'
Date:
"""

from app import Application
from _session import Session

session = Session()
app_ = Application()

session.expire_after = int(app_.conf['global']['session_expired_after'])

log = app_.init_logger('APP')


@app_.route('/host/<host_key>')
def host_cotroller(host_key, **params):
    try:

        if host_key == 'modules':
            return {"result": {"local_host": True, "net_policy_server": True}, "success": True}

        return {'host': 'ok', 'host_key': session.session}
    except StandardError:
        log.exception('Error in host_cotroller')
        return {'success': False, 'errorMessage': 'server_error'}

@app_.route('/netpolicy/<netpolicy_key>')
@app_.route('/netpolicy/profile/<profile_id>')
def netpolicy_controller(netpolicy_key=None, profile_id=None, **params):
    try:

        return {'netpolicy': 'ok', 'netpolicy_key': profile_id}

    except StandardError:
        log.exception('Error in netpolicy_controller')
        return {'success': False, 'errorMessage': 'server_error'}


@app_.route('/login', methods=['POST'])
def user_login(**params):

    login = params.get('login')
    password = params.get('password')
    if not login or not password:
        return {'success': False, 'errorMessage': 'login or pass is missing'}

    if params['login'] in ('yac', 'yac1'):

        if not params.get('session_id', None):
            params['session_id'] = session.generate()

        session.set(params['session_id'], params['login'])

        return {'success': True, 'session': session.session}
    else:
        return {'success': False, 'errorMessage': 'user_not_found'}

@app_.route('/logout', methods=['POST'])
def user_logout(**params):
    if params.get('session_id'):
        session.delete(params['session_id'])

        return {'success': True}

@app_.route('/test/post/<_id>', methods=['POST'])
def test_post(_id=None, **params):
    return {'success': 'post ok', 'params': _id}

