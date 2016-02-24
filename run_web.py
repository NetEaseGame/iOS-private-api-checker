#coding=utf-8
'''
Created on 2015年11月05日
iOS private api检查 Web启动入口
@author: atool
'''


from app import app
if __name__ == '__main__':
    app.run('0.0.0.0', 9527, debug = True,  threaded = True)