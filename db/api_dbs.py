#coding=utf-8
'''
Created on 2015年10月27日

@author: hzwangzhiwei
'''
from db.sqlite_utils import SqliteHandler

#批量插入有文档的api
def insert_apis(table_name, datas):
    sql = "insert into " + table_name + "(api_name, class_name, type, header_file, sdk, framework) values(:api_name, :class_name, :type, :header_file, :sdk, :framework)"
    return SqliteHandler().exec_insert_many(sql, datas)


def delete_apis_by_sdk(table_name, sdk):
    sql = "delete from " + table_name + " where sdk = ?;"
    return SqliteHandler().exec_update(sql, (sdk, ))


