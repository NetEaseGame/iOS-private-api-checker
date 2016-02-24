#coding=utf-8
'''
Created on 2015年1月28日

@author: atool
'''
from functools import wraps

from flask import request, redirect, url_for
from flask.globals import session



def login_required(f):
    '''
    need login wrap
    '''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'u_id' not in session or session['u_id'] is None or session['u_id'] == '':
            return redirect(url_for('login', next = request.url))
        return f(*args, **kwargs)
    return decorated_function