#coding=utf-8
'''
Created on 2015年10月27日

@author: hzwangzhiwei
'''
from db.sqlite_utils import SqliteHandler

#批量插入有文档的api
def insert_document_dbs(datas):
    sql = "insert into document_apis(api_name, class_name, type, header_file, sdk, framework) values(:api_name, :class_name, :type, :header_file, :sdk, :framework)"
    return SqliteHandler().exec_insert_many(sql, datas)


def delete_document_by_sdk(sdk):
    sql = "delete from document_apis where sdk = ?;"
    return SqliteHandler().exec_update(sql, (sdk, ))


