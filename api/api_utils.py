#coding=utf-8
'''
Created on 2015年10月27日
Framework下的头文件里的api = 有文档的api + 没有文档的api
@author: hzwangzhiwei
'''
from db import dsidx_dbs
import os

def framework_dump_header_apis(sdk, framework_folder):
    '''
    class-dump Framework下的库生成的头文件中的api
    sdk: sdk version
    info: 用class-dump对所有的公开库(/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator7.0.sdk/System/Library/Frameworks)进行逆向工程得到所有的头文件内容。提取每个.h文件中的api得到api集合set_A。
    '''
    pass

def framework_header_apis(sdk, framework_folder):
    '''
    get all public frameworks' header files(documented)
    '''
    def iterate_dir(framework, prefix, path):
        files = []
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)):
                files.append((framework, prefix + f, os.path.join(path, f)))
            elif os.path.isdir(os.path.join(path, f)):
                files += iterate_dir(framework, prefix + f + "/", os.path.join(path, f))
        return files
    all_headers = []

    for framework in os.listdir(framework_folder):
        if framework.endswith(".framework"):
            header_path = framework_folder + framework +"/Headers/"
            if os.path.exists(header_path):
                #for header in os.listdir(header_path):
                #    file_path = header_path + header
                #    allpaths.append((framework, header, file_path))
                all_headers += iterate_dir(framework, "", os.path.join(framework_folder, header_path))
                
    return all_headers

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

def private_framework_apis(sdk):
    '''
    PrivateFramework下的api
    '''
    pass 

def all_private_apis(sdk):
    pub_private_apis = framework_dump_header_apis(sdk) - document_apis(sdk) - undocument_apis(sdk)
    
    pri_private_apis = private_framework_apis(sdk)
    
    return pub_private_apis + pri_private_apis