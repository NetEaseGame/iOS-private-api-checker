#coding=utf-8
'''
Created on 2015年6月16日
all tasks
@author: atool
'''
from app.wraps.async_task_wrap import async_task


@async_task
def count_to_10000():
    '''
    test async_task, count to 1w
    注意：在uwsgi部署情况下，不能执行异步任务，所有任务在一次请求完成之后，全部释放
    '''
    for i in xrange(10000):
        print i

