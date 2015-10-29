#coding=utf-8
'''
Created on 2015年10月27日
各种api的获取方式，最后通过这些api计算出私有api的集合，用来后续计算app中是否使用私有api
@author: hzwangzhiwei
'''
from db import dsidx_dbs
import os
import api
from api import api_helpers
from dump import class_dump_utils
from itertools import groupby

def framework_dump_apis(sdk, framework_folder):
    '''
    class-dump Framework下的库生成的头文件中的api
    sdk: sdk version
    info: 用class-dump对所有的公开库(/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator7.0.sdk/System/Library/Frameworks)进行逆向工程得到所有的头文件内容。提取每个.h文件中的api得到api集合set_A。
    '''
#     cur_dir = os.getcwd()
#     pub_headers_path = os.path.join(cur_dir, "tmp/pub-headers")
#     #讲frame dump到./tmp/pub_headers目录中
#     for framework in os.listdir(framework_folder):
#         if framework.endswith(".framework"):
#             frame_path = os.path.join(framework_folder, framework)
#             out_path = os.path.join(pub_headers_path, framework)
#             out_path =  os.path.join(out_path, 'Headers') #构造目录结果： /tmp/xxx.framework/Headers/xx.h
#             rst = class_dump_utils.dump_framework(frame_path, out_path)
#             print rst, out_path

    #分析frame，将头文件输出到tmp/pub-headers目录
    framework_header_folder = _dump_frameworks(framework_folder, 'pub-headers')
#     all_header_paths = []
#     
#     #分析处理后framework .h文件，获得api
#     for framework in os.listdir(pub_headers_path):
#         if framework.endswith(".framework"):
#             header_path = os.path.join(pub_headers_path, framework)
#             if os.path.exists(header_path):
#                 all_header_paths += iterate_dir(framework, "", header_path)
    
    #得到.h文件
    all_headers = _get_headers_from_path(framework_header_folder)
    #解析文件内容，获得api
    framework_apis = _get_apis_from_headers(sdk, all_headers)
    
    return framework_apis
    
    
def framework_header_apis(sdk, framework_folder):
    '''
    get all public frameworks' header files(documented)
    '''
    all_headers = _get_headers_from_path(framework_folder)
    
    framework_apis = _get_apis_from_headers(sdk, all_headers)
               
    return framework_apis

#没有文档的api
def undocument_apis(sdk):
    '''
    info:不在文档中的api方法
    '''
    framework_header_apis(sdk) - document_apis(sdk)

#有文档的api
def document_apis(sdk, db_path):
    '''
    has document apis
    info:获得带文档的api。(/Users/sngTest/Library/Developer/Shared/Documentation/DocSets/com.apple.adc.documentation.AppleiOS7.0.iOSLibrary.docset/Contents/Resources),在里面有个docSet.dsidx的文件，这就是Xcode针对api做的数据库，从这里可以获得带文档的api的各种信息了，从而有了带文档的api集合set_B。
    
    '''
    doc_apis = []
    #从dsidx 数据库中获得初始数据
    apiset = dsidx_dbs.get_dsidx_apis(db_path)
    #过滤初始数据获得有文档的api集合
    for api in apiset:
        Z_PK = api['Z_PK']
        ZDECLAREDIN = api['ZDECLAREDIN']
        # get containername from ZCONTAINER table
        container_name = ''
        if Z_PK:
            container_name = dsidx_dbs.get_container_name(Z_PK, db_path) or ''
            # get frameworkname and headerpath from ZHEADER table
        
        framework_name = ''
        header_path = ''
        if ZDECLAREDIN:
            frame_header = dsidx_dbs.get_framework_and_header(ZDECLAREDIN, db_path)
            if frame_header:
                framework_name = frame_header.get('ZFRAMEWORKNAME', '')
                header_path = frame_header.get('ZHEADERPATH', '')
                
        doc_apis.append({'api_name': api['ZTOKENNAME'], 'class_name': container_name, 'type': api['ZTOKENTYPE'], 'header_file': header_path, 'framework': framework_name, 'sdk': sdk})
    return doc_apis

def private_framework_dump_apis(sdk, framework_folder):
    '''
    PrivateFramework下的api
    '''
    framework_header_folder = _dump_frameworks(framework_folder, 'pri-headers')
    #得到.h文件
    all_headers = _get_headers_from_path(framework_header_folder)
    #解析文件内容，获得api
    framework_apis = _get_apis_from_headers(sdk, all_headers)
    
    return framework_apis 

def all_private_apis(sdk):
    '''
    info: 私有的api ＝ (
            class-dump Framework下的库生成的头文件中的api 
                - 
            (Framework下的头文件里的api = 有文档的api + 没有文档的api)
        ) 
        + 
        PrivateFramework下的api。
    '''
    pub_private_apis = framework_dump_header_apis(sdk) - framework_header_apis(sdk)
    
    pri_private_apis = private_framework_apis(sdk)
    
    return pub_private_apis + pri_private_apis



#目录迭代器
def iterate_dir(framework, prefix, path):
    files = []
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)):
            files.append((framework, prefix + f, os.path.join(path, f)))
        elif os.path.isdir(os.path.join(path, f)):
            files += iterate_dir(framework, prefix + f + "/", os.path.join(path, f))
    return files

#从framework目录，获得所有的.h文件
def _get_headers_from_path(framework_folder):
    all_headers_path = []
    
    frameworks = os.listdir(framework_folder)
    print frameworks
    for framework in frameworks:
        if framework.endswith(".framework"):
            header_path = os.path.join(os.path.join(framework_folder, framework), 'Headers')
            if os.path.exists(header_path):
                all_headers_path += iterate_dir(framework, "", os.path.join(framework_folder, header_path))
    
    return all_headers_path


def _get_apis_from_headers(sdk, all_headers):
    framework_apis = []
    for header in all_headers:
        #get apis from .h file
        apis = api_helpers.get_apis_of_file(header[2])
        
        for api in apis:
            class_name = api["class"] if api["class"] != "ctype" else header[1]
            method_list = api["methods"]
            m_type = api["type"]
            for m in method_list:
                tmp_api = {}
                tmp_api['api_name'] = m
                tmp_api['class_name'] = class_name
                tmp_api['type'] = m_type
                tmp_api['header_file'] = header[1]
                tmp_api['sdk'] = sdk
                tmp_api['framework'] = header[0]
                framework_apis.append(tmp_api)
               
    return framework_apis

#使用calss-dump分析framework目录，将.h文件输出到对应的目录
def _dump_frameworks(framework_folder, prefix):
    cur_dir = os.getcwd()
    headers_path = os.path.join(cur_dir, "tmp/" + prefix)
    
    #讲frame dump到./tmp/pub_headers目录中
    for framework in os.listdir(framework_folder):
        if framework.endswith(".framework"):
            frame_path = os.path.join(framework_folder, framework)
            out_path = os.path.join(headers_path, framework)
            out_path =  os.path.join(out_path, 'Headers') #构造目录结果： /tmp/xxx.framework/Headers/xx.h
            class_dump_utils.dump_framework(frame_path, out_path)
    return headers_path


#api去重
def deduplication_api_list(apis):
    
    def api_gourpby(api):
        return api['api_name'] + '/' + api['class_name']
    
    new_apis = []
    
    apis = sorted(apis, key = api_gourpby)

    for g, l in groupby(api, key = api_gourpby):
        print g
        print list(l)
        if l and len(l) > 0:
            new_apis.append(l[0])
    
    return new_apis