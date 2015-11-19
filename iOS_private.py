#coding=utf-8
'''
Created on 2015年10月27日
iOS private api检查入口
@author: hzwangzhiwei
'''
import os, shutil
from utils import report_utils, utils
from dump import otool_utils, codesign_utils
from api import app_utils, api_utils
from db import api_dbs
# from app.utils import IpaParse
from app.utils import checkipa

def get_executable_path(ipa_path, pid):
    '''
    info: unzip ipa, get execute app path
    '''
    if not os.path.exists(ipa_path):
        #不存在，返回检查结果为空值
        return False
    cur_dir = os.getcwd()
    dest = os.path.join(cur_dir, 'tmp/' + pid)
    if not os.path.exists(dest):
        os.mkdir(dest)
    app_path = app_utils.unzip_ipa(ipa_path, dest) #解压ipa，获得xxx.app目录路径
    app = app_utils.get_executable_file(app_path)

    return app

#检查私有api，返回三个参数
def check_private_api(app, pid):
    strings = app_utils.get_app_strings(app, pid) #一般是app中的一些可打印文本
    #app中的私有库和公有库 .framework
    private, _ = otool_utils.otool_app(app)
    
    app_varibles = app_utils.get_app_variables(app, pid)

    left = strings - app_varibles #去除一些关键字，剩余app中的一些关键词
    
    api_set = api_dbs.get_private_api_list() #数据库中的私有api，去除了whitelist白名单
    print 'private length:', len(api_set)
    inter_api = api_utils.intersection_list_and_api(left, api_set) # app中的api和数据库中的私有api取交集，获得app中的私有api关键字数据

    app_methods = app_utils.get_app_methods(app, pid) #app中的方法名
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
    methods_not_in_app = inter_api # inter_method - methods_in_app # 不在app中的私有方法
    
    return methods_in_app, methods_not_in_app, private

#检查架构，返回架构数组
def check_architectures(app):
    arcs = app_utils.check_architectures(app)
    return arcs

#检查xcode ghost，返回bool
def check_xcode_ghost(app):
    return app_utils.check_xcode_ghost(app)

#检查info和provision文件，并获取建议和错误配置
def check_app_info_and_provision(ipa):
    return checkipa.process_ipa(ipa)

#检查codesign信息
def check_codesign(app):
    return codesign_utils.codesignapp(app)

#ipa的md5
def get_file_md5(ipa):
    return app_utils.file_md5(ipa)


def batch_check(app_folder, excel_path):
    '''
    批量检测多个ipa，并产生excel报告
    '''
    #遍历folder，找出.ipa文件
    if not app_folder or not excel_path:
        return False

    check_results = []
    ipa_list = os.listdir(app_folder)
    for ipa in ipa_list:
        result = {} #每个app的检查结果
        print 'start check :', ipa
        if ipa.endswith('.ipa'):
            ipa_path = os.path.join(app_folder, ipa)
            pid = utils.get_unique_str()
            print 'get_file_md5', '+' * 10
            result['md5'] = get_file_md5(ipa_path)

            print 'check_app_info_and_provision', '+' * 10
            rsts = check_app_info_and_provision(ipa_path)
            for key in rsts.keys():
                result[key] = rsts[key]
            #检查ios私有api
            print 'check_private_api', '+' * 10
            app = get_executable_path(ipa_path, pid)
            if not app:
                #找不到math-o文件，说明不是正常的ipa，忽略
                continue

            methods_in_app, methods_not_in_app, private = check_private_api(app, pid)
            result['private_apis'] = methods_in_app
            result['private_frameworks'] = list(private)
            #检查ipa 64支持情况
            print 'check_architectures', '+' * 10
            arcs = check_architectures(app)
            result['arcs'] = arcs
            #检查ghost情况
            print 'check_xcode_ghost', '+' * 10
            ghost = check_xcode_ghost(app)
            result['ghost'] = ghost
            #检查codesign
            print 'check_private_api', '+' * 10
            codesign = check_codesign(app)
            result['codesign'] = codesign

            check_results.append(result)

            cur_dir = os.getcwd() #删除检查临时目录
            dest_tmp = os.path.join(cur_dir, 'tmp/' + pid)
            if os.path.exists(dest_tmp):
                shutil.rmtree(dest_tmp)


    #将结果转化成excel报告
    report_utils.excel_report(check_results, excel_path)
    return excel_path

if __name__ == '__main__':
    #######
    #check one app
    # ipa_path = "/Users/summer-wj/code/svn/ljsg_for_netease_20150928_resign.ipa"
    
    # private_1 = open("tmp/private_1.txt", "w")
    # private_2 = open("tmp/private_2.txt", "w")
    # #将strings内容输出到文件中
    # pid = app_utils.get_unique_str()
    # app = get_executable_path(ipa_path, pid)
    # print app
    # arcs = check_architectures(app)
    # print arcs
    # a, b, c = check_private_api(app, pid)
    # print "=" * 50
    # print len(a), "Private Methods in App:"
    # print "*" * 50
    # for aa in a:
    #     print aa
    #     print >>private_1, aa
     
    # print "=" * 50
    # print len(b), "Private Methods not in App, May in Framework Used:"
    # print "*" * 50
    # for bb in b:
    #     print >>private_2, bb
     
    # print "=" * 50
    # print len(c), "Private Framework in App:"
    # print "*" * 50

    ##########
    #test batch check ipa
    cwd = os.getcwd()
    excel_path = os.path.join(cwd, 'tmp/' + utils.get_unique_str() + '.xlsx')
    # excel_path = os.path.join(cwd, 'tmp/test.xlsx') # for test
    print excel_path
    # ipa_folder = '/Users/netease/Downloads/ipas/mg/'
    ipa_folder = '/Users/netease/Music/iTunes/iTunes Media/Mobile Applications/'
    print batch_check(ipa_folder, excel_path)

    #########
    #test check arcs
    # app_path = '/Users/netease/Downloads/ipas/mg/Payload'
    # app = app_utils.get_executable_file(app_path)
    # print check_architectures(app)

