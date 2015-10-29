#coding=utf-8
'''
Created on 2015年10月27日
class-dump操作类
@author: hzwangzhiwei
'''
import subprocess

class_dump_path = "/Users/summer-wj/code/svn/iOS-private-api-checker/class-dump" #class-dump所在的位置

dump_cmd = class_dump_path + " -H %s -o %s" # dump cmd模板字符串

def dump_framework(frame_path, out_path):
    '''
    info:使用class-dump来解开framework中的api
    '''
    cmd = dump_cmd % (frame_path, out_path)
    ret = subprocess.call(cmd.split())
    if ret != 0:
        return frame_path
    return ""
    
def dump_app(app_path):
    '''
    get all private variables, properties, and interface name
    '''
    class_dump = class_dump_path + " %s" % app_path
    dump_result = subprocess.check_output(class_dump.split())
    return dump_result