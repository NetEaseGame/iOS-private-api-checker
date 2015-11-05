#coding=utf-8
'''
Created on 2015年6月16日

@author: hzwangzhiwei
'''
from app import app
from app.utils import StringUtil, PathUtil, OtherUtil, IpaParse
import flask
from flask.globals import request
from werkzeug.utils import secure_filename
import os
import iOS_private

@app.route('/', methods=['GET'])
def index_page():
    return flask.render_template('main/index_page.html')


allow_ext = ['ipa']
#ipa上传
@app.route('/ipa_post', methods=['POST'])
def ipa_post():
    rst = {}
    
    upload_file = request.files['file']
    fname = secure_filename(upload_file.filename)
    suffix_name = fname.split('.')[-1]
    #文件后缀名不对时，不做存储处理
    if not suffix_name in allow_ext:
        rst['success'] = 0
        rst['success'] = 'file ext is not allowed'
    else:
        #为图片名称添加时间戳，防止不同文件同名
        fname = StringUtil.get_unique_str() + '.' + suffix_name
        ipa_path = os.path.join(PathUtil.upload_dir(), fname)
        upload_file.save(ipa_path)
        rst['success'] = 1
        rst['data'] = {}
        #获得ipa信息
        ipa_parse = IpaParse.IpaParse(ipa_path)
        rst['data']['app_name'] = ipa_parse.app_name()
        rst['data']['version'] = ipa_parse.version()
        rst['data']['bundle_identifier'] = ipa_parse.bundle_identifier()
        rst['data']['target_os_version'] = ipa_parse.target_os_version()
        rst['data']['minimum_os_version'] = ipa_parse.minimum_os_version()
        #检查ios私有api
        methods_in_app, methods_not_in_app, private = iOS_private.check(ipa_path)
        rst['data']['methods_in_app'] = methods_in_app
        rst['data']['private_framework'] = list(private)
        os.remove(ipa_path)
    #print rst
    return OtherUtil.object_2_dict(rst)

#定义404页面
@app.errorhandler(404)
def page_not_found(error):
    return '404'

@app.errorhandler(502)
def server_502_error(error):
    return '502'


@app.route('/not_allow', methods=['GET'])
def deny(error):
    return 'You IP address is not in white list...'