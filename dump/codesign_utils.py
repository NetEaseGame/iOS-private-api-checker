#coding=utf-8
'''
Created on 2015年11月17日

@author: hzwangzhiwei
'''

import subprocess



def codesignapp(app_path):
    """
    Get codesign informatiob included in app
    About codesign: https://developer.apple.com/legacy/library/technotes/tn2250/_index.html#//apple_ref/doc/uid/DTS40009933
    Args:
        Mach-o path
    Returns:
        the content of codesign
    """

    codesign_cmd = "codesign -dvv %s" # codesign cmd模板字符串
    cmd = codesign_cmd % app_path
    out = subprocess.check_output(cmd.split())
    return out