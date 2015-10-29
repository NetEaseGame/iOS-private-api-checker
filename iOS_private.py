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

def check(ipa_path):
    if not os.path.exists(ipa_path):
        #不存在，返回检查结果为空值
        return [], []
    cur_dir = os.getcwd()
    dest = os.path.join(cur_dir, 'tmp')
    app_path = app_utils.unzip_ipa(ipa_path, dest) #解压ipa，获得xxx.app目录路径
    print app_path
    
    app = app_utils.get_executable_file(app_path)
    print app
    
    strings = app_utils.get_app_strings(app) #一般是app中的一些可打印文本
    
    #app中的私有库和公有库 .framework
    private, public = otool_utils.otool_app(app)
    
    app_varibles = app_utils.get_app_variables(app)
    
    left = strings - app_varibles #去除一些关键字，剩余app中的一些关键词
    
    api_set = api_dbs.get_private_api_list() #数据库中的私有api
    inter = api_utils.intersection_api(left, api_set) # app中的api和数据库中的私有api取交集，获得app中的私有api关键字数据
    
    app_methods = app_utils.get_app_methods(app) #app中的方法名
    
    methods_in_app = api_utils.intersection_api(inter, app_methods) #app中的私有方法
    methods_not_in_app = []#inter - methods_in_app # 不在app中的私有方法
    
    return methods_in_app, methods_not_in_app, private


if __name__ == '__main__':
    ipa_path = "/Users/summer-wj/code/svn/iOS-private-api-scanner/ljsg.ipa"
#     cur_dir = os.getcwd()
#     dest = os.path.join(cur_dir, 'tmp')
#     app_path = app_utils.unzip_ipa(ipa_path, dest)
#     print app_path
    a, b, c = check(ipa_path)
    print "=" * 50
    print len(a), "Private Methods in App:"
    print "*" * 50
    for aa in a:
        print aa
     
    print "=" * 50
    print len(b), "Private Methods not in App, May in Framework Used:"
    print "*" * 50
    for bb in b:
        print bb
     
    print "=" * 50
    print len(c), "Private Framework in App:"
    print "*" * 50
    #for cc in c:
    #    print cc
