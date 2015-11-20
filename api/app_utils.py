#coding=utf-8
'''
Created on 2015年10月29日

@author: hzwangzhiwei
'''
import re
import os, time, datetime, random
import subprocess
from api import api_helpers
from dump import class_dump_utils
import zipfile
from hashlib import md5

def unzip_ipa(ipa_path, dest_path):
    '''
    unzip a ipa, and return the zip folder
    '''
    file_zip = zipfile.ZipFile(ipa_path, 'r')
    for f in file_zip.namelist():
        file_zip.extract(f, dest_path)
    file_zip.close()
    return os.path.join(dest_path, 'Payload')

def get_executable_file(path):
    '''
    info:从ipa中解压出Payload目录中的xxx.app，扫描其中的文件，寻找 Mach-O 文件的路径
    '''

    cmd = u"python -mmacholib find %s" % (path)
    out = subprocess.check_output(cmd.split())
    if out:
        out = out.split()
        if out and len(out) > 0:
             return os.path.join(path, out[0])
    return False
    


def get_app_strings(app_path, pid):
    """
    Args:
        app : the full path of the Mach-O file in app
    Returns:
        output : the result of the strings app
        
    info:strings - 显示文件中的可打印字符
    strings 的主要用途是确定非文本文件的包含的文本内容。
    """
    cmd = "/usr/bin/strings %s" % app_path
    output = subprocess.check_output(cmd.split())
    
    return set(output.split())


def get_dump_result(app):
    """
    get app class-dump result, and cache it
    """
    dump_result = class_dump_utils.dump_app(app)
    return dump_result

def get_app_variables(dump_result, pid):
    "get all variables, properties, and interface name"
    interface = re.compile("^@interface (\w*).*")
    protocol = re.compile("@protocoli (\w*)")
    private = re.compile("^\s*[\w <>]* [*]?(\w*)[\[\]\d]*;")
    prop = re.compile("@property\([\w, ]*\) (?:\w+ )*[*]?(\w+); // @synthesize \w*(?:=([\w]*))?;")
    res = set()
    lines = dump_result.split("\n")
    wait_end = False 
    for line in lines:
        l = line.strip()
        if l.startswith("}"):
            wait_end = False
            continue
        if wait_end:
            r = private.search(l)
            if r:
                res.add(r.groups()[0])
            continue
        r = interface.search(l)
        if r:
            res.add(r.groups()[0])
            wait_end = True
            continue
        r = protocol.search(l)
        if r:
            res.add(r.groups()[0])
            wait_end = True
            continue
        r = prop.search(l)
        if r:
            m = r.groups()
            res.add(m[0])
            res.add("set" + m[0].title() + ":")
            #print "set" + m[0].title() + ":"
            if m[1] != None:
                # res.add("V"+m[1])
                res.add(m[1])
    return res


def get_app_methods(dump_result, pid):
    '''
    info:获得app中的方法
    '''
    # dump_result = class_dump_utils.dump_app(app)
    methods = api_helpers.extract(dump_result)
    #for m in methods:
    #    ret_methods = ret_methods.union(set(m["methods"]))
    #保留class_name信息
    return methods


def check_architectures(app):
    '''
    info检查是否支持64位
    demo:armv7, arm64, armv7s
    '''
    from macholib import MachO, mach_o

    m = MachO.MachO(app)
    arcs = []
    for header in m.headers:
        cpu_type = header.header.cputype
        cpu_subtype = header.header.cpusubtype
        arch = str(mach_o.CPU_TYPE_NAMES.get(cpu_type, cpu_type)).lower()
        if cpu_type == 12:
            if cpu_subtype == 0:
                arch = 'armall'
            elif cpu_subtype == 5:
                arch = 'armv4t'
            elif cpu_subtype == 6:
                arch = 'armv6'
            elif cpu_subtype == 7:
                arch = 'armv5tej'
            elif cpu_subtype == 8:
                arch = 'arm_xscale'
            elif cpu_subtype == 9:
                arch = 'armv7'
            elif cpu_subtype == 10:
                arch = 'armv7f'
            elif cpu_subtype == 11:
                arch = 'armv7s'
            elif cpu_subtype == 12:
                arch = 'armv7k'
            elif cpu_subtype == 13:
                arch = 'armv8'
            elif cpu_subtype == 14:
                arch = 'armv6m'
            elif cpu_subtype == 15:
                arch = 'armv7m'
            elif cpu_subtype == 16:
                arch = 'armv7em'
            
        elif cpu_type == 16777228:
            arch = 'arm64'

        arcs.append(arch)
    return arcs


#检查app是否被xcode ghost感染
xcode_ghost_keyword = "icloud-analysis.com"
def check_xcode_ghost(app):
    cmd = "/usr/bin/strings %s" % app
    output = subprocess.check_output(cmd.split())
    output = output.replace("\n", "")
    output = output.replace(" ", "")
    output = output.replace("\t", "")
    
    return xcode_ghost_keyword in output
    
#获得文件的md5值，便于在检测之后，判断检测文件和上传文件是否对应
def file_md5(file_path):
    m = md5()
    f = open(file_path, 'rb')
    m.update(f.read())
    return m.hexdigest()

def get_unique_str():
    #随机的名字，可以用于上传文件等等不重复，但有一定时间意义的名字
    datetime_str = time.strftime('%Y%m%d%H%M%S',time.localtime())
    return datetime_str + str(datetime.datetime.now().microsecond / 1000) + str(random.randint(0, 1000))
