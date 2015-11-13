#coding=utf-8
'''
Created on 2015年11月13日

@author: hzwangzhiwei
'''
import utils
from lib import xlsxwriter

import sys
reload(sys)
sys.setdefaultencoding('utf8')

def report_detail_sheet(result, excel):
    '''
    info:生成游戏检查的详细信息，每个app一页
    '''
    detail_sheet = excel.add_worksheet(result.get('name', '无名字'))
    detail_sheet.write(0, 0, result.get('bundle_id', ''))
    return excel

def report_outline_sheet(private_results, excel):
    '''
    info: 生成概览的sheet页面，显示app检测的一些概要信息
    '''
    ouline_sheet = excel.add_worksheet('Outline')
    header_style = excel.add_format({'bold': True, 'align': 'center'})
    header_style.set_border(1)   #定义format_title对象单元格边框加粗(1像素)的格式
    header_style.set_bg_color('#cccccc')
     
    ouline_sheet.set_column('A:A', 10)
    ouline_sheet.set_column('B:B', 70)
    #header
    ouline_sheet.write(0, 0, 'ID', header_style)
    ouline_sheet.write(0, 1, '名称', header_style)
    
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
#             private_apis = result.get('private_apis', [])
#             private_frameworks = result.get('private_frameworks', [])
#             
#             arcs = result.get('arcs', [])
#             ghost = result.get('ghost', False)
#             name = result.get('name', '')
#             version = result.get('version', '')
#             bundle_id = result.get('bundle_id', '')
            excel = report_detail_sheet(result, excel)
        excel.close()
    else:
        return False
    

if __name__ == '__main__':
    test_results = []
    #私有api情况
    for i in xrange(10):
        #每一个app的测试结果为一个result
        result = {}
        result['private_apis'] = []
        result['private_frameworks'] = []
        
        result['arcs'] = []
        
        result['ghost'] = False
        if i % 2:
            result['ghost'] = True
        
        result['name'] = '测试游戏' + str(i)
        result['version'] = '426.12'
        result['bundle_id'] = 'com.netease.h' + str(i)
        result['icon'] = '/home/...'
        
        test_results.append(result)
    #test report excel
    excel_path = utils.get_unique_str() + '.xlsx'
    print excel_path
    excel_report(test_results, excel_path)
    print 'gen success~'