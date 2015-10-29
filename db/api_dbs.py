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


def get_private_api_list():
    sql = "select * from private_apis group by api_name;"
    params = ()
    return SqliteHandler().exec_select(sql, params)


#获得所有的私有框架dump出来的api
def get_private_framework_dump_apis(sdk):
    sql = "select * from private_framework_dump_apis where sdk = ?"
    params = (sdk, )
    return SqliteHandler().exec_select(sql, params)

#获得所有的共有框架dump出来的api
def get_framework_dump_apis(sdk):
    sql = "select * from framework_dump_apis where sdk = ?"
    params = (sdk, )
    return SqliteHandler().exec_select(sql, params)


def is_api_exist_in(table_name, api_name, api_class, sdk):
    sql = "select * from " + table_name + " where api_name = ? and class_name = ? and sdk = ?;"
    params = (api_name, api_class, sdk)
    return SqliteHandler().exec_select_one(sql, params)