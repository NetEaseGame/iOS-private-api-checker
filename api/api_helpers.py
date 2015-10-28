#coding=utf-8
'''
Created on 2015年10月27日

@author: hzwangzhiwei
'''
import re


def get_apis_of_file(filepath):
    """
    get the methods of file
    Args:
        header file path(absolute)
    Returns:
        methods list
    """
    with open(filepath) as f:
        text = f.read()
        apis = extract(text)
        return apis
    return []

def remove_comments_old(text):
    """ remove c-style comments.
        text: blob of text with comments (can include newlines)
        returns: text with comments removed
    """
    pattern = r"""
                            ##  --------- COMMENT ---------
           //*              ##  Start of /* ... */ comment
           [^*]*\*+         ##  Non-* followed by 1-or-more *'s
           (                ##
             [^/*][^*]*\*+  ##
           )*               ##  0-or-more things which don't start with /
                            ##    but do end with '*'
           /                ##  End of /* ... */ comment
         |                  ##  -OR-  various things which aren't comments:
           (                ## 
                            ##  ------ " ... " STRING ------
             "              ##  Start of " ... " string
             (              ##
               \\.          ##  Escaped char
             |              ##  -OR-
               [^"\\]       ##  Non "\ characters
             )*             ##
             "              ##  End of " ... " string
           |                ##  -OR-
                            ##
                            ##  ------ ' ... ' STRING ------
             '              ##  Start of ' ... ' string
             (              ##
               \\.          ##  Escaped char
             |              ##  -OR-
               [^'\\]       ##  Non '\ characters
             )*             ##
             '              ##  End of ' ... ' string
           |                ##  -OR-
                            ##
                            ##  ------ ANYTHING ELSE -------
             .              ##  Anything other char
             [^/"'\\]*      ##  Chars which doesn't start a comment, string
           )                ##    or escape
    """
    regex = re.compile(pattern, re.VERBOSE|re.MULTILINE|re.DOTALL)
    noncomments = [m.group(2) for m in regex.finditer(text) if m.group(2)]
    #result = [line for line in noncomments if line.strip()]
    return "".join(noncomments)

def remove_comments(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return ""
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)

def get_c_func(text):
    """
    get c style fucntions
    Args:
        header file content
    Returns:
        function list
        [{'type': 'C/C++', 'ctype': ['CTGetCoreTextVersion']}]
    """
    # delete struct and enum declariations
    del_struct_enum = r"""
        (?:typedef)?\s*struct\s*\w+\s*{[^}]*}\s*\w*;   # struct
        |
        \s*enum\s*{[^}]*\s*};  # enum
        |
        \s*{[^{}]*\s*}     #  function implement
    """
    del_regex = re.compile(del_struct_enum, re.VERBOSE|re.MULTILINE|re.DOTALL)
    text = re.sub(del_regex, "", text)
    #print "C:", text
        #^[^#()]+?([^*\s]+)\s*\((?![^()]*(\d+_\d+|NA)[^)]*\))
    #pattern = r"""
    #    #^(?!\#)(?!\#if)(?!typedef\s\w+).*?(\w+)\s*\((?!\w+,)(?![^()]*(?:\d+_\d+|NA))
    #    ^(?!\#)(?!typedef\s\w+).*?(\w+)\s*\((?!\w+,)(?![^()*^]*(?:\d+_\d+|NA))
    #    |
    #    \([*^]([^)]+)\)\s*\(
    #    |
    #    #\#define\s*([^(#'\n]+)\(  
    #    \#define\s*(\w+)\s?\(\s*\w+
    #"""
    pattern = r"""
        #^(?!\#)(?!\s*typedef\s\w+).*?(\w+)\s*\((?!\w+,)(?![^()*^]*(?:\d+_\d+|NA))
        ^(?!\#)(?!\s*typedef\s\w+).*?(\w+)\s*\((?!\w+,)(?!\d+_\d+|NA,)
        |
        \([*^]([^)]+)\)\s*\(
        |
        \#define\s*(\w+)\s?\(\s*\w*
    """
    #regex = re.compile(pattern)
    regex = re.compile(pattern, re.VERBOSE|re.MULTILINE)
    #regex = re.compile(pattern, re.VERBOSE|re.MULTILINE|re.DOTALL)
    #regex = re.compile(pattern, re.MULTILINE)
    #method = [m.group(1) for m in regex.finditer(text) if m.group(1)]
    #method = [m.group(0) for m in regex.finditer(text) if m.group(0)]
    #method = re.findall(regex, text)
    method = []
    for mm in regex.finditer(text):
        m = mm.groups()
        if m[0]:
            method.append(m[0])
        elif m[1]:
            method.append(m[1])
        elif m[2]:
            method.append(m[2])
    s = set(method)
    method = list(s)
    if len(method) > 0:
        return [{"class":"ctype", "methods":method, "type":"C/C++"}]
    else:
        return []

def get_objc_func(text):
    """ get objective-c style fucntions
    Args:
        header file content
    Returns:
        function list
        [{'UIAlertView': ['textFieldAtIndex:',...], 'type': 'interface'} ]
    """
    def _get_methods(text):
        method = re.compile("([+-] \([ *\w]*\).*?;)\s*")
        #method_args = re.compile("(\w+:)\([\w *^()]*\)\w+ ?")
        method_args = re.compile("(\w+:)")
        #method_no_args = re.compile("[+-] \(.*?\)(\w*)(?:\s*\S*);")
        #method_no_args = re.compile("[+-] \([\w *]+\)\s*(\w*)\s*")
        method_no_args = re.compile("[+-] \([\w *]+\)\s*(\w+)(?!:)")
        temp = []
        for m in method.finditer(text):
            if m:
                #temp.append(m.groups()[0])
                mline = m.groups()[0]
                args = re.findall(method_args, mline)
                if len(args) > 0:
                    temp.append("".join(args))
                else:
                    no_args = method_no_args.search(mline)
                    if no_args:
                        temp.append(no_args.groups()[0])
        return temp
    # remove protocol like: @protocol XXXX, XXXX;
    #print "before:", text
    remove_pro = re.compile("@protocol [\w ,]*;", )
    text = re.sub(remove_pro, "", text)
    #print "after:",text
    interface = r"""
        @interface\s*
        .*?
        @end
    """
    #@protocol\s*\w*\s*(?:<.*?>)\s*
    protocol = r"""
        @protocol\s*
        .*?
        @end
    """
    #class_name = re.compile("@interface\s*(\S*)")
    class_name = re.compile("@interface\s*([\s\(\)\w]*)")
    inter_reg = re.compile(interface, re.VERBOSE|re.MULTILINE|re.DOTALL)
    methods = []
    classes = [m.group(0) for m in inter_reg.finditer(text) if m.group(0)]
    for c in classes:
        cm = class_name.search(c)
        if cm:
            cn = cm.groups()[0].replace(" ", "")
            cn = cn.strip()
        temp = _get_methods(c)
        if temp:
            methods.append({"class":cn, "methods":temp, "type":"interface"})

    protocol_reg = re.compile(protocol, re.VERBOSE|re.MULTILINE|re.DOTALL)
    protocols = [m.group(0) for m in protocol_reg.finditer(text) if m.group(0)]
    valid_protocol = re.compile("@protocol\s*[\w, ]*;")
    protocol_name = re.compile("@protocol\s*(\w*)")
    for p in protocols:
        valid = valid_protocol.search(p)
        if valid:
            continue
        else:
            #print p
            pm = protocol_name.search(p)
            if pm:
                pn = pm.groups()[0]
            temp = _get_methods(p)
            if temp:
                methods.append({"class":pn, "methods":temp, "type":"protocol"})

    #print methods
    return methods

def remove_objc(text):
    """
    remove interface and protocls
    """
    p = r"""
        @interface
        .*?
        @end
        |
        @protocol
        .*?
        @end
    """
    pattern = re.compile(p, re.VERBOSE|re.MULTILINE|re.DOTALL)
    return re.sub(pattern, "", text)


def extract(text):
    no_comment_text = remove_comments(text)
    methods = []
    #if no_comment_text.count("@interface") > 0 or no_comment_text.count("@protocol") > 0:
    #   methods = get_objc_func(no_comment_text)
    #else:
    #    methods = get_c_func(no_comment_text)
    methods += get_objc_func(no_comment_text)
    no_class = remove_objc(no_comment_text)
    methods += get_c_func(no_class)
    return methods


#not used
def extract_pri(filename):
    struct = re.compile("^struct (\w*).*")
    typedef = re.compile("^} (\w*);")
    method = re.compile("^[+-] \([ *\w]*\)\w+[;:].*")
    method_args = re.compile("(\w+:)\([\w *]*\)\w+ ?")
    method_no_args = re.compile("^[+-] \( *\w*\)(\w*);")
    interface = re.compile("^@interface (\w*).*")
    result = set()
    f = open(filename)
    for line in f:
        m = method.search(line)
        if m:
            args = re.findall(method_args, line)
            if len(args) > 0:
                result.add("".join(args))
            else:
                no_args = method_no_args.search(line)
                if no_args:
                    result.add(no_args.groups()[0])
            continue
    f.close()
    return result

if __name__ == '__main__':
    pri = extract_pri('E:/Eclipse_WS/iOS-private-api-checker/tmp/Frameworks/UIKit.framework/Headers/UIToolbar.h')
    
    print list(pri)
    
    pub = get_apis_of_file('E:/Eclipse_WS/iOS-private-api-checker/tmp/Frameworks/UIKit.framework/Headers/UIToolbar.h')
    print pub[0]['methods']