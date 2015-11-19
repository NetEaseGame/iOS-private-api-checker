#coding=utf-8
'''
Created on 2015年11月17日

@author: hzwangzhiwei
'''

import commands



def codesignapp(app_path):
    """
    Get codesign informatiob included in app
    About codesign: https://developer.apple.com/legacy/library/technotes/tn2250/_index.html#//apple_ref/doc/uid/DTS40009933
    Args:
        Mach-o path
    Returns:
        the content of codesign
    """
    cmd = "/usr/bin/codesign -dvvv %s" % app_path
    out = commands.getstatusoutput(cmd)
    if out and len(out) == 2 and out[0] == 0:
        out = out[1]
    else:
        out = ''
    return out