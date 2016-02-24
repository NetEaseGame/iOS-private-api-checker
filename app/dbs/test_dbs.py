#coding=utf-8
'''
Created on 2015年8月25日

@author: atool
'''
from app.dbs.inc.Redis import RedisMysqlCache
from app.dbs.inc.Mysql import Mysql


#获取tid的测试信息
def get_test_by_id(test_id, use_redis_cache = True):
    sql = "select * from abtest_tests where test_id = %s"
    params = (test_id, )
    
    #该方法你用redis缓存
    if use_redis_cache:
        return RedisMysqlCache().select_one(sql, params)
    else:
        return Mysql().exec_select_one(sql, params)

if __name__ == '__main__':
    print get_test_by_id(1)
    print get_test_by_id("1", False)