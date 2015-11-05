#coding=utf-8
'''
Created on 2015年10月27日
iOS private api检查入口
@author: hzwangzhiwei
'''
import os
from dump import otool_utils
from api import app_utils, api_utils
from db import api_dbs


def get_executable_path(ipa_path):
    '''
    info: unzip ipa, get execute app path
    '''
    if not os.path.exists(ipa_path):
        #不存在，返回检查结果为空值
        return False
    cur_dir = os.getcwd()
    dest = os.path.join(cur_dir, 'tmp')
    print dest
    app_path = app_utils.unzip_ipa(ipa_path, dest) #解压ipa，获得xxx.app目录路径
    
    app = app_utils.get_executable_file(app_path)
    return app

def check_private_api(app):
    #print app
    strings = app_utils.get_app_strings(app) #一般是app中的一些可打印文本
    #app中的私有库和公有库 .framework
    private, public = otool_utils.otool_app(app)
    
    app_varibles = app_utils.get_app_variables(app)

    left = strings - app_varibles #去除一些关键字，剩余app中的一些关键词
    
    api_set = api_dbs.get_framework_private_apis() #数据库中的私有api
    print 'private length:', len(api_set)
    inter_api = api_utils.intersection_list_and_api(left, api_set) # app中的api和数据库中的私有api取交集，获得app中的私有api关键字数据
    
    app_methods = app_utils.get_app_methods(app) #app中的方法名
    app_apis = []
    for m in app_methods:
        class_name = m["class"] if m["class"] != "ctype" else 'cur_app'
        method_list = m["methods"]
        m_type = m["type"]
        for m in method_list:
            tmp_api = {}
            tmp_api['api_name'] = m
            tmp_api['class_name'] = class_name
            tmp_api['type'] = m_type
            #tmp_api['header_file'] = ''
            #tmp_api['sdk'] = ''
            #tmp_api['framework'] = ''
            app_apis.append(tmp_api)
    
    
    methods_in_app = api_utils.intersection_api(app_apis, inter_api) #app中的私有方法
    methods_not_in_app = inter_api# inter_method - methods_in_app # 不在app中的私有方法
    
    return methods_in_app, methods_not_in_app, private


def check_architectures(app):
    arcs = app_utils.check_architectures(app)
    return arcs



if __name__ == '__main__':
    ipa_path = "/Users/summer-wj/code/svn/ljsg_for_netease_20150928_resign.ipa"
#     cur_dir = os.getcwd()
#     dest = os.path.join(cur_dir, 'tmp')
#     app_path = app_utils.unzip_ipa(ipa_path, dest)
#     print app_path
    
    private_1 = open("tmp/private_1.txt", "w")
    private_2 = open("tmp/private_2.txt", "w")
    #将strings内容输出到文件中

    app = get_executable_path(ipa_path)
    print app
    arcs = check_architectures(app)
    print arcs
    a, b, c = check_private_api(app)
    print "=" * 50
    print len(a), "Private Methods in App:"
    print "*" * 50
    for aa in a:
        print aa
        print >>private_1, aa
     
    print "=" * 50
    print len(b), "Private Methods not in App, May in Framework Used:"
    print "*" * 50
    for bb in b:
        print >>private_2, bb
     
    print "=" * 50
    print len(c), "Private Framework in App:"
    print "*" * 50
    #for cc in c:
    #    print cc
    
