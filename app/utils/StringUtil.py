#coding=utf-8
'''
Created on 2015年6月16日

@author: hzwangzhiwei
'''
import time
import datetime
import random

def is_empty(s):
    if s == None or s == '':
        return True
    return False


def get_unique_str():
    #随机的名字，可以用于上传文件等等不重复，但有一定时间意义的名字
    datetime_str = time.strftime('%Y%m%d%H%M%S',time.localtime())
    return datetime_str + str(datetime.datetime.now().microsecond / 1000) + str(random.randint(0, 1000))