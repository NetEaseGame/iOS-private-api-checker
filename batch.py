#coding=utf-8
'''
Created on 2015年10月27日
一些预处理脚本
@author: hzwangzhiwei
'''
from db import api_dbs
from api import api_utils

#重建document api数据库
def rebuild_document_api(sdk, docset):
    #先删除对应的sdk document api数据
    api_dbs.delete_document_by_sdk(sdk)
    
    document_apis = api_utils.document_apis(sdk, docset)
    for api in document_apis:
        print api
        
    return api_dbs.insert_document_dbs(document_apis)


if __name__ == '__main__':
    #重建sdk=7.0的有文档api
    print rebuild_document_api('7.0', 'docSet.dsidx')

    