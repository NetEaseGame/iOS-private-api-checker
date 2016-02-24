#coding=utf-8
'''
Created on 2015年8月21日

@author: atool
'''

import MySQLdb
from app import db_config
import time

import sys
from app.wraps.mysql_escape_warp import mysql_escape

reload(sys)
sys.setdefaultencoding('utf8')

@mysql_escape
def dict_2_sql_conditions(dict_param):
    conditions = []
    p_keys = dict_param.keys()
    for k in p_keys:
        conditions.append(k + " = '" + str(dict_param[k]) + "'")
    
    return " and ".join(conditions)

@mysql_escape
def dict_2_insert_sql(table_name, dict_param):
    key = []
    val = []
    p_keys = dict_param.keys()
    for k in p_keys:
        key.append(k)
        val.append("'" + str(dict_param[k]) + "'")
        
    key = ",".join(key)
    val = ",".join(val)
    sql = "insert into " + table_name + "("+ key+") values (" + val + ");"
    return sql

class Mysql():
    #对象属性
    #连接
    conn = None
    #数据游标
    cursor = None
    
    #构造函数
    def __init__(self, host = db_config['DB_HOST'], 
                        port = db_config['DB_PORT'],
                        user = db_config['DB_USER'], 
                        passwd = db_config['DB_PSW'], 
                        db = db_config['DB_NAME'], 
                        charset = db_config['DB_CHARSET']):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db
        self.charset = charset
        
        self.__connect()
    
    
    def __connect(self):
        try:
            self.conn = MySQLdb.connect(host = self.host, port = self.port, user = self.user, passwd = self.passwd, db = self.db, charset = self.charset)
            #字典形式
            self.cursor = self.conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
#             print("Mysql Connect to %s: %s" % (self.host, str(self.port)))
        except MySQLdb.Error as e:
            print("Mysql Error %s: %s" % (self.host, e.args[1]))
            
    def exec_select(self, sql, params):
        '''
        ps：执行查询类型的sql语句
        '''
        try:
            self.cursor.execute(sql, params)
            result_set = self.cursor.fetchall()
            return result_set
        except MySQLdb.Error as e:
            print("Mysql Error:%s\nSQL:%s" %(e, sql))
            return False
        
    def exec_select_one(self, sql, params):
        '''
        ps：执行查询类型的sql语句
        '''
        try:
            self.cursor.execute(sql, params)
            result_set = self.cursor.fetchone()
            return result_set
        except MySQLdb.Error as e:
            print("Mysql Error:%s\nSQL:%s" %(e, sql))
            return False
    
    def exec_insert(self, sql, params):
        '''
        ps:执行插入类sql语句
        '''
        try:
            # 执行sql语句
            self.cursor.execute(sql, params)
            # 提交到数据库执行
            insert_id = self.conn.insert_id()
            self.conn.commit()
            return insert_id
        except MySQLdb.Error as e:
            print("Mysql Error:%s\nSQL:%s" %(e, sql))
            self.conn.rollback()
            return False
    
    def exec_insert_dict(self, table_name, dict_param):
        '''
        ps:执行插入数据，数据由一个dict给定，key为column名称
        '''
        try:
            sql = dict_2_insert_sql(table_name, dict_param)
            return self.exec_insert(sql, ())
        except MySQLdb.Error as e:
            print("Mysql Error:%s\nSQL:%s" %(e, sql))
            self.conn.rollback()
            return False
    
    def exec_update(self, sql, params):
        '''
        ps:执行更新类sql语句
        '''
        try:
            # 执行sql语句
            self.cursor.execute(sql, params)
            row_count = self.cursor.rowcount
            # 提交到数据库执行
            self.conn.commit()
            if row_count == False:
                row_count = True
            return row_count
        except MySQLdb.Error as e:
            print("Mysql Error:%s\nSQL:%s" %(e, sql))
            self.conn.rollback()
            return False
    ###################
    ###################
    def exec_sql(self, sql, params):
        try:  
            n = self.cursor.execute(sql, params)  
            return n  
        except MySQLdb.Error as e:  
            print("Mysql Error:%s\nSQL:%s" %(e, sql))

    def get_last_insert_id(self):
        '''
        ps:最后插入行id
        '''
        return self.conn.insert_id()
    
    def get_influence_row_count(self):
        '''
        ps:影响函数
        '''
        return self.cursor.rowcount  
    #for transation
    
    def commit(self):
        '''
        PS:事物完成之后，commit
        '''
        self.conn.commit()
    
#     @check_connect    
    def rollback(self):
        '''
        PS:事物失败之后，回退
        '''
        self.conn.rollback()
    #end for transation
    ###################
    
    def close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None

#test        
if __name__ == '__main__':
    start = time.time()
    for i in xrange(100):
        sql = "insert into abtest_users(user_type) values(%s)"
        params = (str(i), )
        Mysql().exec_insert(sql, params)
    
    end = time.time()
    print '多连接：', 100 / (end - start)
    
    start = time.time()
    my = Mysql()
    for i in xrange(100):
        sql = "insert into abtest_users(user_type) values(%s)"
        params = (str(i), )
        my.exec_insert(sql, params)
        
    end = time.time()
    print '单连接：', 100 / (end - start)
    