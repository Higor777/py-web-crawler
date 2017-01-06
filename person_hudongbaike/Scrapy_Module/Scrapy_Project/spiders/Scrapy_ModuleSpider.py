# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("Scrapy_Module/")

from Scrapy_Project.items import Scrapy_ModuleItem
import scrapy
from bs4 import BeautifulSoup
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
import os
import logging  

from collections import OrderedDict
from Scrapy_Project import Reference_Data
from category import GetUrlPool,getAllSubCategory

class Scrapy_ModuleSpider(scrapy.Spider):
    name = "Scrapy_ModuleSpider"
    allowed_domains = ["baike.com"]
    start_urls = []
    CrawledURL = []
    RecordedURL = []
    RecordedFileName = None
    RecordedFile = None
    URLPool = []
    infoKeyMap = {}
    realKeyMap = {}
    openCatp = []
    figureRelation = {}
    categoryOriginalList = []
    categoryList = []
    subCategoryMap = {}
    start_urls_length = 0
    responseCount = 0
    personCount = 0
    logger = None
    def __init__(self,categorylist = []):
        self.logger = logging.getLogger('Scrapy_Module') # 获取名为Scrapy_Module的logger 
        self.categoryOriginalList = categorylist
        self.infoKeyMap = OrderedDict(Reference_Data.infoKeyMapList)
        self.realKeyMap = OrderedDict(Reference_Data.realKeyMapList)
        result_dir = os.path.split(os.path.realpath(__file__))[0]+'/../result/'
        file_dir = result_dir + 'RecordedURL/'
        self.RecordedFileName = file_dir+'RecordedURL'#+category
        if not os.path.exists(result_dir):
            os.mkdir(result_dir)
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)
        self.RecordedFile = open(self.RecordedFileName,'a+')
        Recorded_line = self.RecordedFile.readline().strip().lstrip().rstrip('\n')
        while Recorded_line:
            #print Recorded_line
            self.RecordedURL.append(Recorded_line)
            Recorded_line = self.RecordedFile.readline().strip().lstrip().rstrip('\n')
        self.RecordedFile.close()
        for category in self.categoryOriginalList :
            self.logger.debug("Finding SubCategory in Category " + category + '...')
            self.subCategoryMap[category] = getAllSubCategory(category)
            for categoryTemp in self.subCategoryMap[category] :
                if categoryTemp not in self.categoryList:
                    self.categoryList.append(categoryTemp)
            self.logger.debug("Finding StartURL in Category " + category + '...')
            urlPool = []
            urlPool = GetUrlPool(category)
            length = len(urlPool)
            self.start_urls_length = self.start_urls_length + length
            if length > 0:
                self.start_urls = self.start_urls + urlPool
                self.logger.debug("Category " + category + ' has ' + str(length) + ' URL')
            else:
                self.logger.debug("No URL in Category " + category)
        #print self.start_urls

    def parse(self, response):
        html_doc = response.body 
        html_doc = html_doc.decode('utf-8')
        self.soup = BeautifulSoup(html_doc,'html.parser')
        [script.extract() for script in self.soup.findAll('script')]#去除网页中的script内容
        [style.extract() for style in self.soup.findAll('style')]#去除网页中的css内容
        itemTemp = {}
        info_table = {}
        info_key = ''
        info_len = 0
        baseifno = {}
        person_flag = None
        table = []

        self.responseCount = self.responseCount + 1
        print '|---本次已访问：',self.responseCount,'个页面---|---新增目标人物信息',self.personCount,'条---|'
        #定位‘开放分类’,将开放分类放入self.openCatp
        self.getOpenCatp()
        #检查‘开放分类’中是否含有需要查找的分类
        if self.isOpenCatpInList():
            #检查网页中所有的table，是否有人物信息
            table = self.soup.table
            while table != None:
                info_key = '' 
                for string in table.stripped_strings:
                    if '：' == string[-1]:
                        #最后一个字符为‘：’（中文），则是一个新的key
                        info_key = string[0:-1].replace(" ","")
                        baseifno[info_key] = ''
                    elif info_key :
                        #info_key不为空
                        baseifno[info_key] = baseifno[info_key] + string     
                table = table.find_next('table')
            #for i in baseifno:
                #print i,':',baseifno[i]

            #Is a person ?
            if self.isPerson(baseifno):
                item = self.getItem(response,baseifno)
                #for i in item:
                    #print i,':',item[i]
                if item['cururl'] not in self.RecordedURL:
                    with open(self.RecordedFileName,'a+') as self.RecordedFile:
                        self.RecordedFile.write(item['cururl']+'\n')
                    self.RecordedURL.append(item['cururl'])
                    if len(item['category']) > 0:
                        self.personCount = self.personCount + 1
                        yield item
                #在人物页面搜索链接，将可能是人物的链接放入地址池，后续跟进这些地址
                self.getURL(response)

        #在responseCount大于start_urls_length的70%后跟进可能是人物的地址
        #目的为提升爬取前期目标人物命中率
        if self.responseCount > self.start_urls_length*0.9:
            for url in self.URLPool:
                self.URLPool.remove(url)
                if url not in self.CrawledURL:
                    self.CrawledURL.append(url)
                    yield Request(url,callback=self.parse)

    #判断是不是人物信息
    def isPerson(self,info):
        if info :
            if '中文名' in info or '姓名' in info :
                if '出生年月' in info :
                    return True
                if '国籍' in info :
                    return True
                if '性别' in info :
                    return True
        return False

    #生成item
    def getItem(self,response,info):
        item = Scrapy_ModuleItem()
        item['cururl'] = response.url
        item['category'] = []
        for openCatpkey in self.openCatp :
            for categoryKey in self.subCategoryMap.keys():
                if openCatpkey in self.subCategoryMap[categoryKey] :
                    if categoryKey not in item['category']:
                        item['category'].append(categoryKey)
        #获取人物关系，配偶，儿女，并因此判断婚姻状态
        self.getFigureRelation()
        for key in self.realKeyMap.keys():
            if key in info.keys():
                keyTemp = self.infoKeyMap[self.realKeyMap[key]]
                #之前没有给key赋值
                if keyTemp not in item.keys() :
                    item[keyTemp] = info[key].replace(',',' ')
                    if keyTemp == 'height' :
                        item[keyTemp] = item[keyTemp].replace('cm','')
                        item[keyTemp] = item[keyTemp].replace('厘米','')
                    elif keyTemp == 'blood' :
                        item[keyTemp] = item[keyTemp].replace('型','')
                    elif keyTemp == 'weight' :
                        item[keyTemp] = item[keyTemp].replace('kg','')
                    elif keyTemp == 'people' :
                        item[keyTemp] = item[keyTemp].replace('族','')
                    elif keyTemp == 'nationality' :
                        if '中华人民' in item[keyTemp]:
                            item[keyTemp] = '中国'
        if self.figureRelation['配偶'] :
           item['spouse'] = self.figureRelation['配偶']
        if self.figureRelation['儿女'] :
           item['children'] = self.figureRelation['儿女']
        if self.figureRelation['配偶'] or self.figureRelation['儿女'] :
            item['marriage'] = '#已婚'
        if 'religion' not in item.keys() and 'politics' in item.keys():
            if '共产' in item['politics']:
                item['religion'] = '#共产主义'
        if 'education' not in item.keys() and 'school' in item.keys():
            for keyWord in Reference_Data.educationKeyWord['大学']:
                if keyWord in item['school']:
                    item['education'] = '#本科以上'
            for keyWord in Reference_Data.educationKeyWord['高中']:
                if keyWord in item['school']:
                    item['education'] = '#高中以上'
            for keyWord in Reference_Data.educationKeyWord['初中']:
                if keyWord in item['school']:
                    item['education'] = '#初中以上'
            for keyWord in Reference_Data.educationKeyWord['小学']:
                if keyWord in item['school']:
                    item['education'] = '#小学以上'
        if 'occupation' not in item.keys() and 'job' in item.keys():
            if '军' in item['job']:
                item['occupation'] = '#军事家'
            elif '政' in item['job']:
                item['occupation'] = '#政治家'
            elif '思' in item['job']:
                item['occupation'] = '#思想家'
            elif '医' in item['job']:
                item['occupation'] = '#医学家'
            elif '农' in item['job']:
                item['occupation'] = '#农学家'
            elif '演' in item['job'] or '歌' in item['job']:
                item['occupation'] = '#艺人'
            else:
                item['occupation'] = '#其他'
        if 'household' not in item.keys() and 'origin' in item.keys():
            item['household'] = '#' + item['origin']
        if 'dynasty' not in item.keys() and 'birthdate' in item.keys():
            if '年' in item['birthdate']:
                year = item['birthdate'][0:item['birthdate'].find('年')]
                if '公元' in year:
                    if '公元前' in year:
                        year = year.replace('公元前','')
                        try:
                            year = -int(year)
                        except Exception,e:
                            print 'Exception: ',e
                    else:
                        year = year.replace('公元','')
                        try:
                            year = int(year)
                        except Exception,e:
                            print 'Exception: ',e
                else:
                    try:
                        year = int(year)
                    except Exception,e:
                        print 'Exception: ',e
            if type(year) == type(1):
                item['dynasty'] = self.getDynasty(year)
        return item

    #获取人物关系
    def getFigureRelation(self):
        self.figureRelation['配偶'] = []
        self.figureRelation['儿女'] = []
        for idtemp in ['fi_opposite','holder1']:
            relationTable = self.soup.find(id = idtemp)
            relationTable = BeautifulSoup(str(relationTable))
            relation_li = relationTable.li
            while relation_li:
                relation_li_list =  list(relation_li.stripped_strings)
                if len(relation_li_list) == 2:
                    if idtemp == 'fi_opposite':
                        for relationKey in self.figureRelation.keys():
                            for keyWord in Reference_Data.relationKeyWord[relationKey]:
                                if keyWord in relation_li_list[1] and relation_li_list[0] not in self.figureRelation[relationKey]:
                                    self.figureRelation[relationKey].append(relation_li_list[0])
                                    break
                    elif idtemp == 'holder1':
                        relationKey = '儿女'
                        for keyWord in Reference_Data.relationKeyWord[relationKey]:
                            if keyWord in relation_li_list[1] and relation_li_list[0] not in self.figureRelation[relationKey]:
                                self.figureRelation[relationKey].append(relation_li_list[0])
                                break
                relation_li = relation_li.find_next('li')
        #将列表转换为字符串
        for relationKey in self.figureRelation.keys():
            string = ''
            for i in self.figureRelation[relationKey]:
                string = string + i + '/'
            string = string[0:-1]
            self.figureRelation[relationKey] = string
            #print relationKey + ' : ' + string

    #人物链接判断
    #姓名判断，只是判断姓
    def url_filter(self,name,linkhref):
        if 'javascript' not in linkhref :
            if 'wiki' in linkhref or ('&prd=citiao_so' in linkhref and linkhref[-1] == 'o'):
                if len(name) < 7:
                    if len(name) > 1 and name[0] in Reference_Data.Surnames :
                        return True
                    elif len(name) > 2 and name[0:2] in Reference_Data.Surnames :
                        return True
        return False

    #获取网页内链接，并作一定处理与去重
    def getURL(self,response):
        itemTemp = self.soup.findAll('a')#获取网页内所有链接
        base_url = get_base_url(response)
        for obj in itemTemp:
            linkhref = obj.get('href')
            if linkhref:
                linkhref = urljoin_rfc(base_url, linkhref)
                if obj.text and self.url_filter(obj.text,linkhref):
                    #print obj.text
                    #http://www.baike.com/sowiki/%E8%BF%9F%E6%B5%A9%E7%94%B0?prd=content_doc_search
                    if 'sowiki' in linkhref:
                        linkhref = linkhref.replace('sowiki','wiki').replace('?prd=content_doc_search','')
                    #
                    if 'tongyici' in linkhref:
                        linkhref = linkhref.replace('sowiki','wiki').replace('?prd=zhengwenye_left_tongyici','')
                    #http://so.baike.com/doc/%E8%BF%9F%E6%98%9F%E5%8C%97&amp;prd=citiao_so
                    if 'so' in linkhref and 'doc' in linkhref:
                        linkhref = linkhref.replace('doc','wiki')
                        linkhref = linkhref.replace('&prd=citiao_so','')
                        linkhref = linkhref.replace('so','www')
                    if linkhref in self.URLPool or linkhref in self.CrawledURL :
                        continue
                    else :
                        #print linkhref
                        self.URLPool.append(linkhref)
            
    #定位‘开放分类’
    def getOpenCatp(self) :
        self.openCatp = []
        p = self.soup.find(id='openCatp')
        if p:
            for p_category in p.stripped_strings:
                if '开放分类' not in p_category :
                    self.openCatp.append(p_category)
        #for str in self.openCatp:
            #print str

    #判断是否为目标分类
    def isOpenCatpInList(self):
        for openCatpkey in self.openCatp :
            if openCatpkey in self.categoryList :
                return True
        return False

    #获取朝代
    def getDynasty(self,year):
        for dynasty in Reference_Data.dynastyMap.keys():
            if year >= Reference_Data.dynastyMap[dynasty][0] and year < Reference_Data.dynastyMap[dynasty][1]:
                return '#' + dynasty
        return '#不明'