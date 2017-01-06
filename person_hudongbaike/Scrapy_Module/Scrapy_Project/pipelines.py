# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import logging  
import logging.handlers
from collections import OrderedDict


from Scrapy_Project import Reference_Data

from database import PersonDatabase

#将结果存入数据库
class Scrapy_ModulePipelineSql(object):
    def __init__(self):
        pass

    def process_item(self, item, spider):
        Database = PersonDatabase()
        Database.insert(item)
        Database.showDatabaseInfo()
        Database.close()
        return item

#将结果写入文件，逗号分隔，弃用
class Scrapy_ModulePipelineCsv(object):
    filenameMap = {}
    CountfileNameMap = {}
    resultfile = None
    Countfile = None
    Count = 0
    encode_w = 'utf-8'
    logger = None
    infoKeyMap = None
    itemKeyList = ['category']
    keyString = ''
    key = ''
    targetCount = {}
    def __init__(self):
        self.infoKeyMap = OrderedDict(Reference_Data.infoKeyMapList)
        for value in self.infoKeyMap.values():
            if value not in self.itemKeyList :
                self.itemKeyList.append(value)
        self.logger = logging.getLogger('Scrapy_Module') # 获取名为Scrapy_Module的logger 
        result_dir = os.path.split(os.path.realpath(__file__))[0] + '/result/'
        file_dir = result_dir+'personInfoCSV/'
        for category in Reference_Data.categoryList :
            self.filenameMap[category] = file_dir+category+'_person_info.csv'
            self.CountfileNameMap[category] = file_dir+category+'Count' 
            self.targetCount[category] = 0
        if not os.path.exists(result_dir):
            os.mkdir(result_dir)
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)
        for filename in self.filenameMap.values() :
            if not os.path.isfile(filename):
                keyString = ''
                for key in self.infoKeyMap.keys():
                    if keyString:
                        keyString = keyString + ',' + key
                    else:
                        keyString = keyString + key
                keyString = keyString + ',url\n'
                try:
                    with open(filename,'w') as self.resultfile:
                        self.resultfile.write(keyString.encode(self.encode_w))
                except Exception,e:
                    self.logger.error("ERROR:Write result file failed.")
                    self.logger.error(e)
        for key in self.CountfileNameMap.keys() :
            filename = self.CountfileNameMap[key]
            if os.path.isfile(filename):
                try:
                    with open(filename,'r') as self.Countfile:
                        self.targetCount[key] = int(self.Countfile.readline())
                except Exception,e:
                    self.logger.error("ERROR:Read count file failed.")
                    self.logger.error(e)
            else:
                try:
                    with open(filename,'w') as self.Countfile:
                        self.Countfile.write(str(self.targetCount[key]))
                except Exception,e:
                    self.logger.error("ERROR:Write count file failed.")
                    self.logger.error(e)

    def process_item(self, item, spider):
        string = ''
        for key in self.infoKeyMap.values():
            if key in item.keys():
                string =  string + item[key]
            string =  string + ','
        string = string[0:-1]
        string =  string + ',' +item['cururl'] +'\n'
        string = string.encode(self.encode_w)
        for itemCategory in item['category']:
            self.filename = self.filenameMap[itemCategory]
            self.CountfileName = self.CountfileNameMap[itemCategory]
            try:
                with open(self.filename,'a+') as self.resultfile :
                    self.resultfile.write(string)
                self.targetCount[itemCategory] = self.targetCount[itemCategory] + 1
            except Exception,e:
                self.logger.error("ERROR:Write result file failed.")
                self.logger.error(e)
            try:
                with open(self.CountfileName,'w') as self.Countfile:
                    self.Countfile.write(str(self.targetCount[itemCategory]))
            except Exception,e:
                self.logger.error("ERROR:Write Count file failed.")
                self.logger.error(e)
        for Category in Reference_Data.categoryList:
            print Category,':',self.targetCount[Category]
        return item








