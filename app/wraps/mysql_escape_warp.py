#coding=utf-8
'''
Created on 2015年3月30日

@author: hzwangzhiwei
'''

from functools import wraps
import types

import MySQLdb

#对字典经典转义
def _str_escape(s, d):
    if s == None:
        return ''
    return MySQLdb.escape_string(s)

def _no_escape(s, d):
    if s == None:
        return ''
    return s

def mysql_escape(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        newargs = []
        #先转义参数，再执行方法
        for arg in args:
            #字符串，包括中文
            if type(arg) is types.StringType or type(arg) is types.UnicodeType:
                newargs.append(MySQLdb.escape_string(arg))
            
            #字典    
            elif isinstance(arg, dict):
                newargs.append(MySQLdb.escape_dict(arg, {
                                                         types.StringType: _str_escape,
                                                         types.UnicodeType: _str_escape,
                                                         types.IntType: _no_escape,
                                                         types.FloatType: _no_escape
                                                         }))
            #其他类型不转义
            else:
                newargs.append(arg)
                
        newargs = tuple(newargs)
        
        func = f(*newargs, **kwargs)
        
        return func
    return decorated_function