#coding=utf-8
'''
Created on 2015年11月13日

@author: hzwangzhiwei
'''
import utils
from lib import xlsxwriter

import sys
from lib.xlsxwriter.utility import xl_rowcol_to_cell_fast
reload(sys)
sys.setdefaultencoding('utf8')

def report_detail_sheet(result, excel):
    '''
    info:生成游戏检查的详细信息，每个app一页
    '''
    #app check info
    name = result.get('name', '')
    version = result.get('version', '')
    bundle_id = result.get('version', '')
    tar_version = result.get('tar_version', '')
    min_version = result.get('min_version', '')
    private_apis = result.get('private_apis', '')
    private_frameworks = result.get('private_frameworks', '')
    ghost = result.get('ghost', '')
    arcs = result.get('arcs', '')
    
    detail_sheet = excel.add_worksheet(result.get('name', '无名字'))
    #title
    title_style = excel.add_format({'bold': True, 'align': 'center', 'font_size': 16, 'valign': 'vcenter', 'fg_color': '#fff2cc'})
    detail_sheet.merge_range('A1:J2', 'APP检查报告 - ' + name, title_style)
    
    #app infomation show
    header_style = excel.add_format({'bold': True, 'align': 'center', 'fg_color': '#b6d7a8', 'border': 1})
    text_style = excel.add_format({'align': 'center', 'border': 1})
    
    detail_sheet.set_column('A:J', 17)
    
    detail_sheet.write(2, 0, '游戏名字', header_style) #A
    detail_sheet.write(2, 1, name, text_style) #B
    
    detail_sheet.write(2, 2, '游戏版本', header_style) #C
    detail_sheet.write(2, 3, version, text_style) #D
    
    detail_sheet.write(2, 4, 'Bundle ID', header_style) #E
    detail_sheet.write(2, 5, bundle_id, text_style) #F
    
    detail_sheet.write(2, 6, 'Target Version', header_style) #G
    detail_sheet.write(2, 7, tar_version, text_style) #H
    
    detail_sheet.write(2, 8, 'Min Version', header_style) #I
    detail_sheet.write(2, 9, min_version, text_style) #J
    
    #xcode ghost & arcs
    
    #ghost
    detail_sheet.merge_range('A4:B4', 'Xcode Ghost', header_style)
    detail_sheet.write('C4:C4', ghost, text_style)
    #arcs
    detail_sheet.merge_range('D4:E4', 'Architectures', header_style)
    detail_sheet.merge_range('F4:J4', ' / '.join(arcs), text_style)
    
    sub_title_style = excel.add_format({'bold': True, 'align': 'center', 'font_size': 14, 'valign': 'vcenter', 'fg_color': '#d9ead3', 'border': 1})
    
    #private api
    base_row = 5
    detail_sheet.merge_range(base_row, 0, base_row, 9, 'Private API 私有API调用情况', sub_title_style)
    base_row = base_row + 1
    
    table_header_style = excel.add_format({'bold': True, 'align': 'center', 'fg_color': '#fff2cc'})
    
    detail_sheet.write(base_row, 0, '#', table_header_style)
    detail_sheet.write(base_row, 1, 'Framework', table_header_style)
    detail_sheet.write(base_row, 2, 'File', table_header_style)
    detail_sheet.write(base_row, 3, 'Class', table_header_style)
    detail_sheet.merge_range(base_row, 4, base_row, 9, 'API', table_header_style)
    
    cnt = 0
    for api in private_apis:
        base_row = base_row + 1
        cnt  = cnt + 1
        detail_sheet.write(base_row, 0, cnt, text_style)
        detail_sheet.write(base_row, 1, api.get('framework', ''), text_style)
        detail_sheet.write(base_row, 2, api.get('header_file', ''), text_style)
        detail_sheet.write(base_row, 3, api.get('class_name', ''), text_style)
        detail_sheet.merge_range(base_row, 4, base_row, 9, api.get('api_name', ''), text_style)
    
    base_row = base_row + 2
    #private framework使用情况
    detail_sheet.merge_range(base_row, 0, base_row, 9, 'Private API 私有API调用情况', sub_title_style)
    base_row = base_row + 1
    
    detail_sheet.write(base_row, 0, '#', table_header_style)
    detail_sheet.merge_range(base_row, 1, base_row, 9, 'Framework', table_header_style)
    cnt = 0
    for framework in private_frameworks:
        base_row = base_row + 1
        cnt  = cnt + 1
        detail_sheet.write(base_row, 0, cnt, text_style)
        detail_sheet.merge_range(base_row, 1, base_row, 9, framework, text_style)
    return excel

def report_outline_sheet(private_results, excel):
    '''
    info: 生成概览的sheet页面，显示app检测的一些概要信息
    '''
    ouline_sheet = excel.add_worksheet('Outline - 检测结果总览')
    #title
    title_style = excel.add_format({'bold': True, 'align': 'center', 'font_size': 18, 'valign': 'vcenter', 'fg_color': '#b6d7a8'})
    ouline_sheet.merge_range('A1:I3', '手游Appstore上线预审核报告', title_style)
    
    ########header
    header_style = excel.add_format({'bold': True, 'align': 'center', 'fg_color': '#fff2cc'})
    header_style.set_border(1)   #定义format_title对象单元格边框加粗(1像素)的格式
    
    ouline_sheet.set_column('A:A', 5)
    ouline_sheet.set_column('B:B', 20)
    ouline_sheet.set_column('C:D', 15)
    ouline_sheet.set_column('E:F', 20)
    ouline_sheet.set_column('G:H', 15)
    ouline_sheet.set_column('I:I', 50)
    #header
    ouline_sheet.write(3, 0, 'ID', header_style) #A
    ouline_sheet.write(3, 1, '游戏名称', header_style) #B
    
    ouline_sheet.write(3, 2, '版本号', header_style) #C
    ouline_sheet.write(3, 3, 'Bundle ID', header_style) #D
    ouline_sheet.write(3, 4, 'Target os version', header_style) #E
    ouline_sheet.write(3, 5, 'Minimum os version', header_style) #F
    
    ouline_sheet.write(3, 6, '私有API', header_style) #G
    ouline_sheet.write_comment('G4', '私有api是平台禁止使用的一些方法集合，如果app中使用，可能会导致上线被拒，并且给苹果留下不好的印象；此项包括私有API和私有Framework')
    ouline_sheet.write(3, 7, 'XcodeGhost', header_style) #H
    ouline_sheet.write_comment('H4', 'XcodeGhost 为国内xcode下载导致的内嵌代码事件')
    ouline_sheet.write(3, 8, '架构', header_style) #I
    ouline_sheet.write_comment('I4', 'appstore 在2014年底强制要求所有的上线app都必须支持64位架构')
    #header
    
    #data
#     success_format = excel.add_format(({'bold': True, 'color': '#b6d7a8'}))
#     fail_format = excel.add_format(({'bold': True, 'color': '#cc4125'}))
    text_format = excel.add_format(({'align': 'center'}))
    url_format = excel.add_format({'font_color': 'blue', 'underline':  1})
    cnt = 4
    for result in private_results:
        ouline_sheet.write(cnt, 0, cnt - 3, text_format) #A
        name = result.get('name', '')
        ouline_sheet.write(cnt, 1, name) #B
        ouline_sheet.write_url(cnt, 1, 'internal:' + name + '!' + xl_rowcol_to_cell_fast(0, 0), url_format, name) 
        ouline_sheet.write(cnt, 2, result.get('version', ''), text_format) #C
        ouline_sheet.write(cnt, 3, result.get('bundle_id', ''), text_format) #D
        ouline_sheet.write(cnt, 4, result.get('tar_version', ''), text_format) #E
        ouline_sheet.write(cnt, 5, result.get('min_version', ''), text_format) #F
        
        ouline_sheet.write(cnt, 6, str(len(result.get('private_apis', []))) + ' / ' + str(len(result.get('private_frameworks', []))), text_format) #G
        
        ouline_sheet.write(cnt, 7, result.get('ghost', ''), text_format) #H
        ouline_sheet.write(cnt, 8, ' / '.join(result.get('arcs', ''))) #I
        
        cnt = cnt + 1
    
    return excel

def excel_report(private_results, excel_path):
    '''
    info:将批量检查结果转换成excel报告，格式大概为：
        1. 首页是所有app的总揽，比如app信息、app私有api使用数量、app架构、app感染情况等
        2. 其他sheet为app单页详情，具体为app的私有api详情
    
    private_results为数组结构，里面为检查的结果字典
    '''
    if private_results and isinstance(private_results, list):
        
        excel_name = excel_path
        
        excel = xlsxwriter.Workbook(excel_name)
        #增加概览的sheet
        excel = report_outline_sheet(private_results, excel)
        
        for result in private_results:
            excel = report_detail_sheet(result, excel)
        excel.close()
    else:
        return False
    

if __name__ == '__main__':
    #用于测试的数据，数据结果和检查结果一模一样
    test_results = []
    #私有api情况
    for i in xrange(10):
        #每一个app的测试结果为一个result
        result = {}
        result['private_apis'] = []
        result['private_apis'].append({'framework': 'rsst_fr', 'header_file': '/homwefw/wef.haewf', 'class_name': 'wfwefClass', 'api_name': 'wfewefwf'})
        result['private_apis'].append({'framework': 'rsst_fr', 'header_file': '/homwefw/wef.haewf', 'class_name': 'wfwefClass', 'api_name': 'wfewefwf'})
        result['private_frameworks'] = []
        result['private_frameworks'].append('wfwefwefwef.froamfef')
        
        result['arcs'] = ['wef', 'wfwefwfwefwewfe']
        
        result['ghost'] = False
        if i % 2:
            result['ghost'] = True
        
        result['name'] = '测试游戏' + str(i)
        result['version'] = '426.12'
        result['tar_version'] = '426.12a'
        result['min_version'] = '426.12n'
        result['bundle_id'] = 'com.netease.h' + str(i)
        result['icon'] = '/home/...'
        
        test_results.append(result)
    #test report excel
    excel_path = utils.get_unique_str() + '.xlsx'
#     excel_path = 'test.xlsx'
    print excel_path
    excel_report(test_results, excel_path)
    print 'gen success~'