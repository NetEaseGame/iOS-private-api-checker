#coding=utf-8
'''
Created on 2015年10月27日
一些预处理脚本
@author: hzwangzhiwei
'''
from db import api_dbs
from db import other_dbs
from api import api_utils
from config import sdks_config
from api.api_utils import framework_dump_apis

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


def rebuild_sdk_private_api(sdk_version):
    api_dbs.delete_apis_by_sdk('private_apis', sdk_version['sdk'])
#     print rebuild_framework_header_api(sdk_version['sdk'], sdk_version['framework'])
#     print rebuild_dump_framework_api(sdk_version['sdk'], sdk_version['framework'])
#     print rebuild_dump_private_framework_api(sdk_version['sdk'], sdk_version['private_framework'])
    
    #通过计算，获得私有api，并保存到数据库汇总
    #1. private_framework_api 转存到private表中
    private_framework_apis = api_dbs.get_private_framework_dump_apis(sdk_version['sdk'])
    print 'One private api. count: ', api_dbs.insert_apis('private_apis', private_framework_apis)
    #2. framework_dump - framework_header
    #3. framework_dump中_开头的api
    framework_dump_private_apis = []
    framework_dump_apis = api_dbs.get_framework_dump_apis(sdk_version['sdk'])
    
    for api in framework_dump_apis:
        if api['api_name'] and api['api_name'][0:1] == '_':
            print 'api start with `_`'
            framework_dump_private_apis.append(api)
            continue
        #对于不以下划线开头的
        r = api_dbs.is_api_exist_in('framework_header_apis', api['api_name'], api['class_name'], api['sdk'])
        if r:
            print 'api is public in public framework'
            pass
        else:
            print 'api is private in public framework'
            framework_dump_private_apis.append(api)
    framework_dump_private_apis = framework_dump_private_apis + list(private_framework_apis)
    print 'private api lengh:', len(framework_dump_private_apis)
    print 'start group by...'
    framework_dump_private_apis = api_utils.deduplication_api_list(framework_dump_private_apis)
    print 'deduplication private api len:', len(framework_dump_private_apis)
    
    rst = api_dbs.insert_apis('private_apis', framework_dump_private_apis)
    print 'insert into db, len:', rst
    
if __name__ == '__main__':
#     print other_dbs.create_some_table()
#     重建sdk=8.4的有文档api
#     print rebuild_document_api('8.4', 'docSet.dsidx')
    
    for sdk_version in sdks_config:
        rebuild_sdk_private_api(sdk_version)



