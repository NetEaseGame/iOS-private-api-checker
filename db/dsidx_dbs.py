#coding=utf-8
'''
Created on 2015年10月27日
.dsidx 文件解读
@author: atool
'''
from db.sqlite_utils import SqliteHandler
def get_dsidx_apis(db_path):
    '''
    has document apis
    info:获得带文档的api。(/Users/Test/Library/Developer/Shared/Documentation/DocSets/com.apple.adc.documentation.AppleiOS7.0.iOSLibrary.docset/Contents/Resources),在里面有个docSet.dsidx的文件，这就是Xcode针对api做的数据库，从这里可以获得带文档的api的各种信息了，从而有了带文档的api集合set_B。
    
    '''
    sql = "SELECT T.Z_PK, T.ZTOKENNAME, T.ZTOKENTYPE, T.ZCONTAINER, M.ZDECLAREDIN FROM ZTOKEN AS T, ZTOKENMETAINFORMATION AS M WHERE ZTOKENTYPE IN (3,9,12,13,16) AND T.Z_PK = M.ZTOKEN"
    apiset = SqliteHandler(db = db_path).exec_select(sql)
    return apiset


def get_container_name(Z_PK, db_path):
    sql = "SELECT ZCONTAINERNAME FROM ZCONTAINER WHERE Z_PK = ?;"
    container = SqliteHandler(db = db_path).exec_select_one(sql, (Z_PK, ))
    if container:
        return container['ZCONTAINERNAME']
    return None


def get_framework_and_header(Z_PK, db_path):
    sql = "SELECT ZFRAMEWORKNAME, ZHEADERPATH FROM ZHEADER WHERE Z_PK = ?;"
    rst = SqliteHandler(db = db_path).exec_select_one(sql, (Z_PK, ))
    return rst
