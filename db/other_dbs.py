#coding=utf-8
'''
Created on 2015年10月27日

@author: hzwangzhiwei
'''
from db.sqlite_utils import SqliteHandler
def create_some_table():
    #创建framework_header_apis
    sql1 = ("create table framework_dump_header_apis("
           "api_name varchar,"
           "class_name varchar,"
           "type varchar,"
           "header_file varchar,"
           "sdk varchar,"
           "framework varchar)")
    
    
    sql2 = ("create table framework_header_apis("
           "api_name varchar,"
           "class_name varchar,"
           "type varchar,"
           "header_file varchar,"
           "sdk varchar,"
           "framework varchar)")
    
    
    sql3 = ("create table document_apis("
           "api_name varchar,"
           "class_name varchar,"
           "type varchar,"
           "header_file varchar,"
           "sdk varchar,"
           "framework varchar)")
    
    
    sql4 = ("create table undocument_apis("
           "api_name varchar,"
           "class_name varchar,"
           "type varchar,"
           "header_file varchar,"
           "sdk varchar,"
           "framework varchar)")
    
    
    sql5 = ("create table private_apis("
           "api_name varchar,"
           "class_name varchar,"
           "type varchar,"
           "header_file varchar,"
           "sdk varchar,"
           "framework varchar)")
    
    SqliteHandler().exec_sql(sql1, ())
    SqliteHandler().exec_sql(sql2, ())
    SqliteHandler().exec_sql(sql3, ())
    SqliteHandler().exec_sql(sql4, ())
    SqliteHandler().exec_sql(sql5, ())