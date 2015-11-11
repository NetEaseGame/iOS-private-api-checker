#coding=utf-8
'''
Created on 2015年10月27日
一些预处理脚本
@author: hzwangzhiwei
'''
import os
from db import api_dbs
from db import other_dbs
from api import api_utils
from config import sdks_config, sqlite_info
from db import api_dbs
from db import other_dbs
from api import api_utils
from config import sdks_config
from api.api_utils import framework_dump_apis

#重建document api数据库
def rebuild_document_api(sdk, docset):
    '''
    document api
    set_C
    '''
    #先删除对应的sdk document api数据
    api_dbs.delete_apis_by_sdk('document_apis', sdk)
    
    document_apis = api_utils.document_apis(sdk, docset)
    #for api in document_apis:
    #    print api
        
    return api_dbs.insert_apis('document_apis', document_apis)


def rebuild_framework_header_api(sdk, framework_folder):
    '''
    public framework header(.h) api
    set_B
    '''
    api_dbs.delete_apis_by_sdk('framework_header_apis', sdk)
    
    framework_header_apis = api_utils.framework_header_apis(sdk, framework_folder)
    #for api in framework_header_apis:
    #    print api
    
    return api_dbs.insert_apis('framework_header_apis', framework_header_apis)


def rebuild_dump_framework_api(sdk, framework_folder):
    '''
    public framework dump apis
    set_A
    '''
    api_dbs.delete_apis_by_sdk('framework_dump_apis', sdk)
    
    framework_dump_header_apis = api_utils.framework_dump_apis(sdk, framework_folder)
    #for api in framework_dump_header_apis:
    #    print api
    
    return api_dbs.insert_apis('framework_dump_apis', framework_dump_header_apis)

def rebuild_dump_private_framework_api(sdk, framework_folder):
    '''
    private framework dump api
    set_D
    '''
    api_dbs.delete_apis_by_sdk('private_framework_dump_apis', sdk)
    
    pri_framework_dump_apis = api_utils.private_framework_dump_apis(sdk, framework_folder)
    pri_framework_dump_apis = api_utils.deduplication_api_list(pri_framework_dump_apis)
    #for api in pri_framework_dump_apis:
    #    print api
    
    return api_dbs.insert_apis('private_framework_dump_apis', pri_framework_dump_apis)


def rebuild_private_api(sdk, include_private_framework = False):
    '''
    set_E private api
    undocument_api = set_B - set_C
    set_E = set_A - set_C - undocument_api = set_A - set_B
    if include_private_framework: set_E = set_E + set_D
    '''
    # first flush the table data
    api_dbs.delete_apis_by_sdk('framework_private_apis', sdk_version['sdk'])
    api_dbs.delete_apis_by_sdk('private_apis', sdk_version['sdk'])

    framework_dump_private_apis = []
    framework_dump_apis = api_dbs.get_framework_dump_apis(sdk_version['sdk'])
    
    pub_cnt = 0
    pri_cnt = 0
    __cnt = 0
    for api in framework_dump_apis:
        if api['api_name'] and api['api_name'][0:1] == '_':
            __cnt = __cnt + 1
            framework_dump_private_apis.append(api)
            continue
        #对于不以下划线开头的
        r = api_dbs.is_api_exist_in('framework_header_apis', api)
        if r:
            pub_cnt = pub_cnt + 1
        else:
            r = api_dbs.is_api_exist_in('document_apis', api)
            if r:
                pub_cnt = pub_cnt + 1
            else:
                pri_cnt = pri_cnt + 1
                framework_dump_private_apis.append(api)

    print 'pub_cnt:', pub_cnt
    print 'pri_cnt:', pri_cnt
    print '__cnt:', __cnt

    print 'private api lengh:', len(framework_dump_private_apis)
    print 'start group by...'
    #去除重复
    framework_dump_private_apis = api_utils.deduplication_api_list(framework_dump_private_apis)
    print 'deduplication private api len:', len(framework_dump_private_apis)

    rst = api_dbs.insert_apis('private_apis', framework_dump_private_apis)
    print 'insert into db private_apis, len:', rst

    rst = api_dbs.insert_apis('framework_private_apis', framework_dump_private_apis)
    print 'insert into db framework_private_apis, len:', rst

    if include_private_framework:
        private_framework_apis = api_dbs.get_private_framework_dump_apis(sdk_version['sdk'])
        rst = api_dbs.insert_apis('private_apis', framework_dump_private_apis)
        print 'insert into db private_apis, len:', rst
    return True

def rebuild_sdk_private_api(sdk_version, include_private_framework = False):
    #1. set_A public framework dump api
    print 'set_A'
    print rebuild_dump_framework_api(sdk_version['sdk'], sdk_version['framework'])
    #2. set_B public framework .h api
    print 'set_B'
    print rebuild_framework_header_api(sdk_version['sdk'], sdk_version['framework'])
    #3. set_C docset file -> ducument api
    print 'set_C'
    print rebuild_document_api(sdk_version['sdk'], sdk_version['docset'])
    #4. set_D private framework dump api
    print 'set_D'
    print rebuild_dump_private_framework_api(sdk_version['sdk'], sdk_version['private_framework'])

    #5. private api
    rebuild_private_api(sdk_version['sdk'], include_private_framework)
    
    
if __name__ == '__main__':
    #数据库不存在，则创建数据库
    if not os.path.exists(sqlite_info["DB"]):
        print 'db not exists, creating...'
        print other_dbs.create_some_table()
    
    for sdk_version in sdks_config:
        rebuild_sdk_private_api(sdk_version, False)


