#coding=utf-8
'''
Created on 2015年8月21日
数据库、redis连接装饰器，用于view上，给需要数据连接的加上相应的装饰器即可
保证在一次http连接过程中只需要进行一次mysql连接，减少内存占用，减少连接时间
TODO 暂时不用
@author: hzwangzhiwei
'''

from functools import wraps

import MySQLdb
from flask import g
from app import db_config


def _connect_db():
    conn = MySQLdb.connect(host = db_config['DB_HOST'], 
                           user = db_config['DB_USER'], 
                           passwd = db_config['DB_PSW'], 
                           db = db_config['DB_NAME'], 
                           charset = db_config['DB_CHARSET'])
    #字典形式
    cursor = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
    return (conn, cursor)

#获取数据库连接装饰器
def require_db_connection(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ####连接数据库
        if hasattr(g, 'conn') and g.conn != None and hasattr(g, 'cursor') and g.cursor != None:
            print 'has db connect, do nothing'
        else:
            (g.conn, g.cursor) = _connect_db()
            print 'create new db connect'
        
        #执行方法
        func = f(*args, **kwargs)
        
        ###关闭数据库连接
        if hasattr(g, 'conn') and g.conn != None and hasattr(g, 'cursor') and g.cursor != None:
            g.cursor.close()
            g.cursor = None 
            g.conn.close()
            g.conn = None
            print 'close db connect'
        else:
            print 'no db connect, no need to close...'
        
        return func
    return decorated_function

