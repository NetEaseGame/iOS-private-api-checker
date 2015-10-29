#coding=utf-8
'''
Created on 2015年10月29日

@author: hzwangzhiwei
'''

import subprocess
import re

otool_path = "otool" #otool所在的位置

otool_cmd = otool_path + " -L %s" # otool cmd模板字符串

def otool_app(app_path):
    """
    Get framework included in app
    Args:
        Mach-o path
    Returns:
        two sets, one is public framework, one is private framework
    """
    cmd = otool_cmd % app_path
    
    out = subprocess.check_output(cmd.split())
    pattern = re.compile("PrivateFrameworks\/(\w*)\.framework")
    pub_pattern = re.compile("Frameworks\/([\.\w]*)")
    
    private = set()
    public = set()
    
    for r in re.finditer(pattern, out):
        private.add(r.group(1))
        
    for r in re.finditer(pub_pattern, out):
        public.add(r.group(1))
        
    return private, public