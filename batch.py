#coding=utf-8
'''
Created on 2015年10月27日
一些预处理脚本
@author: hzwangzhiwei
'''
from db import api_dbs
from db import other_dbs
from api import api_utils
from time import sleep

#重建document api数据库
def rebuild_document_api(sdk, docset):
    #先删除对应的sdk document api数据
    api_dbs.delete_apis_by_sdk('document_apis', sdk)
    
    document_apis = api_utils.document_apis(sdk, docset)
    for api in document_apis:
        print api
        
    return api_dbs.insert_apis('document_apis', document_apis)


def rebuild_framework_header_api(sdk, framework_folder):
    api_dbs.delete_apis_by_sdk('framework_header_apis', sdk)
    
    framework_header_apis = api_utils.framework_header_apis(sdk, framework_folder)
    for api in framework_header_apis:
        print api
    
    return api_dbs.insert_apis('framework_header_apis', framework_header_apis)


def rebuild_dump_framework_api(sdk, framework_folder):
    api_dbs.delete_apis_by_sdk('framework_dump_apis', sdk)
    
    framework_dump_header_apis = api_utils.framework_dump_apis(sdk, framework_folder)
    for api in framework_dump_header_apis:
        print api
    
    return api_dbs.insert_apis('framework_dump_apis', framework_dump_header_apis)

def rebuild_dump_private_framework_api(sdk, framework_folder):
    api_dbs.delete_apis_by_sdk('private_framework_dump_apis', sdk)
    
    pri_framework_dump_apis = api_utils.private_framework_dump_apis(sdk, framework_folder)
    for api in pri_framework_dump_apis:
        print api
    
    return api_dbs.insert_apis('private_framework_dump_apis', pri_framework_dump_apis)


if __name__ == '__main__':
    #print other_dbs.create_some_table()
    #sleep(5)
    #重建sdk=7.0的有文档api
    #print rebuild_document_api('7.0', 'docSet.dsidx')
    #sleep(5)
    #print rebuild_framework_header_api('7.0', "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator8.4.sdk/System/Library/Frameworks/")

    print rebuild_dump_framework_api('7.0', "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator8.4.sdk/System/Library/Frameworks/")
    #print rebuild_dump_private_framework_api('7.0', "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator8.4.sdk/System/Library/PrivateFrameworks/")




