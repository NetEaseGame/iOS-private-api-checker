#coding=utf-8
'''
Created on 2015年6月16日
main模块涉及的数据库操作
可以是mysql，也可以是mongodb
使用什么数据库，什么orm均不限制
@author: atool
'''


def get_user_by_id(u_id):
    '''
    get the user information
    '''
    #执行sql，获得数据，返回给views层使用
    return {'name':'atool', 'sex': 1}