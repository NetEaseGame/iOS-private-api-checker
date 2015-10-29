#coding=utf-8
'''
Created on 2015年10月27日

@author: hzwangzhiwei
'''

mysql_info = {
    'HOST': '127.0.0.1',
    'PORT': 3306,
    'USERNAME': 'root',
    'PASSWORD': 'root',
    'CHARTSET': 'UTF8',
    'DB': 'ios_private',
}

sqlite_info = {
    'DB': 'ios_private.db',
}

#配置各个不同sdk版本的framework目录，
sdks_config = []
sdks_config.append({
    'sdk': '7.0', 
    'framework': '/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator7.0.sdk/System/Library/Frameworks/', 
    'private_framework': '/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator7.0.sdk/System/Library/PrivateFrameworks/'
})