#coding=utf-8
'''
Created on 2015年8月21日
Mongo db 操作类
TODO Test
@author: hzwangzhiwei
'''
from app import db_config
import pymongo


class Mongo():
    
    #类变量
    DESC = pymongo.DESCENDING
    ASC = pymongo.ASCENDING
    
    def __init__(self, host = db_config['DB_HOST'], 
                        port = db_config['DB_PORT'],
                        user = db_config['DB_USER'], 
                        passwd = db_config['DB_PSW'], 
                        db = db_config['DB_NAME'], 
                        charset = db_config['DB_CHARSET']):
        
        self.connection = pymongo.Connection(host, port)
        self.db = self.connection[db]
        self.db.authenticate(user, passwd)
        
        
    def insert(self, table, params):
        return self.db[table].insert(params)
        
    def save(self, table, params):
        return self.db[table].save(params)
        
    def find(self, table, params = {}, sort = {}, skip = 0, limit = 25):
        if skip == -1:
            skip = 0
        
        if limit < 0:
            return self.db[table].find(params).sort(sort).skip(skip)
        return self.db[table].find(params).sort(sort).limit(limit).skip(skip)
    
    def count(self, table, params):
        return self.db[table].find(params).count()
        
    def find_one(self, table, params = {}):
        return self.db[table].find_one(params)
    
    def remove(self, table, params):
        return self.db[table].remove(params)
        
    def update(self, table, params):
        return self.db[table].update(params)    
    
    #高级应用
    #1. 分页
    def get_page_count(self, table, params = {}, page_size = 25):
        if page_size < 0:
            page_size = 25
        
        total_cnt = self.count(table, params)
        return (total_cnt - 1) / 25 + 1
        
    def find_page(self, table, params = {}, sort = {}, page = 1, page_size = 25):
        page_count = self.get_page_count(table, params, page_size)
        limit = page_size
        
        if page <= 0:
            page = 1
        
        if page > page_count:
            page = page_count
            
        skip = (page - 1) * page_size
        
        return self.find(table, params, sort, skip, limit)
    
    
#test        
if __name__ == '__main__':
    #TODO
    pass