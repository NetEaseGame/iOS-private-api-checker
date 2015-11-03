#coding=utf-8
'''
Created on 2015年11月3日

@author: hzwangzhiwei
'''
import sys
from config import class_dump_z_path


def get_system():
    '''
    get system platform, to define use which class-dump-z
    '''
    system_platform = sys.platform
    if system_platform.startswith('linux'):
        return 'linux'
    elif system_platform.startswith('win32'):
        return 'win'
    elif system_platform.startswith('dawin'):
        return 'mac'
    else:
        return 'iphone'
    
   
def get_clas_dump_path():
    '''
    get class-dump-z path
    '''
    system = get_system()
    return class_dump_z_path.get(system, 'class-dump-z')