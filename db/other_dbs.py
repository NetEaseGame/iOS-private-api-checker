#coding=utf-8
'''
Created on 2015年10月27日

@author: atool
'''
from db.sqlite_utils import SqliteHandler
def create_some_table():
    #从public framework 中dump出来的所有api，其中包含部分私有api（sql7）
    sql1 = ("create table framework_dump_apis("
           "api_name varchar,"
           "class_name varchar,"
           "type varchar,"
           "header_file varchar,"
           "sdk varchar,"
           "framework varchar)")
    
    #从public framework .h文件中解析代码解析出来的api
    sql2 = ("create table framework_header_apis("
           "api_name varchar,"
           "class_name varchar,"
           "type varchar,"
           "header_file varchar,"
           "sdk varchar,"
           "framework varchar)")
    
    #有文档的pi
    sql3 = ("create table document_apis("
           "api_name varchar,"
           "class_name varchar,"
           "type varchar,"
           "header_file varchar,"
           "sdk varchar,"
           "framework varchar)")
    
    #sql2 - sql3
    sql4 = ("create table undocument_apis("
           "api_name varchar,"
           "class_name varchar,"
           "type varchar,"
           "header_file varchar,"
           "sdk varchar,"
           "framework varchar)")
    
    #包括sql6，sql7的所有内容
    sql5 = ("create table private_apis("
           "api_name varchar,"
           "class_name varchar,"
           "type varchar,"
           "header_file varchar,"
           "sdk varchar,"
           "framework varchar)")
    
    #private framework dump出来的api，全部为私有api
    sql6 = ("create table private_framework_dump_apis("
           "api_name varchar,"
           "class_name varchar,"
           "type varchar,"
           "header_file varchar,"
           "sdk varchar,"
           "framework varchar)")

    sql7 = ("create table framework_private_apis("
           "api_name varchar,"
           "class_name varchar,"
           "type varchar,"
           "header_file varchar,"
           "sdk varchar,"
           "framework varchar)")

    sql8 = ("create table whitelist("
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
    SqliteHandler().exec_sql(sql6, ())
    SqliteHandler().exec_sql(sql7, ())
    SqliteHandler().exec_sql(sql8, ())

