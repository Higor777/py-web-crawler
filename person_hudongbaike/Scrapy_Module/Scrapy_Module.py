#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.split(os.path.realpath(__file__))[0])
from Scrapy_Project.spiders.Scrapy_ModuleSpider import Scrapy_ModuleSpider
from Scrapy_Project import Reference_Data

from Scrapy_Project.database import PersonDatabase
# scrapy api
from scrapy import signals
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
import  scrapy.utils.project as Scr_pro
import logging  
import logging.handlers

import commands

class Scrapy_Module(object):
    Scrapy_Module_setting = None
    logfile = ''
    categoryList = []
    finishCnt = 0
    def __init__(self):
        logfileDir = os.path.split(os.path.realpath(__file__))[0] + '/Scrapy_Project/result/'
        self.logfile = logfileDir + 'Scrapy_Module_Person.log'
        if not os.path.exists(logfileDir):
            os.mkdir(logfileDir)
        #记录当前工作用于还原工作目录
        cwd = os.getcwd()
        #获取当前文件所在目录，并把工作目录切换到文件所在目录，用于读取Scrapy项目settings
        file_dir = os.path.split(os.path.realpath(__file__))[0]
        os.chdir(file_dir)
        self.Scrapy_Module_setting = Scr_pro.get_project_settings()
        #关闭打印信息
        self.Scrapy_Module_setting.set('LOG_ENABLED',False)
        fileHandler = logging.handlers.RotatingFileHandler(self.logfile, maxBytes = 1024*1024, backupCount = 5) # 实例化handler   
        streamHandler = logging.StreamHandler()
        #fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'  
        fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(message)s'  
        formatter = logging.Formatter(fmt)                  # 实例化formatter  
        fileHandler.setFormatter(formatter)                 # 为handler添加formatter 
        streamHandler.setFormatter(formatter)               # 为handler添加formatter 
        self.logger = logging.getLogger('Scrapy_Module')    # 获取名为Scrapy_Module的logger  
        self.logger.addHandler(fileHandler)                 # 为logger添加handler  
        self.logger.addHandler(streamHandler)               # 为logger添加handler  
        self.logger.setLevel(logging.DEBUG)  
        self.logger.info('Scrapy_Module Start.')
        #将工作目录还原为之前的工作目录
        os.chdir(cwd)
    def spider_closing(self,spider):
        '''
        #收到Spider结束信号后计数加一，用于同时开启多个Spider
        self.finishCnt = self.finishCnt + 1
        #print self.finishCnt
        #如果Spider全部结束，则关闭reactor
        if self.finishCnt >= len(self.categoryList):
        '''
        self.logger.info("Closing reactor")
        reactor.stop()
        #导出结果文件
        self.logger.info("Export xls and sql File ")
        Database = PersonDatabase()
        Database.exportToXls()
        Database.exportToSql()
        Database.close()


    def crawl(self,List):
        self.categoryList = List
        for category in self.categoryList :
            self.logger.info('crawl : '+category)
        Runner = CrawlerRunner(self.Scrapy_Module_setting)
        #创建Spider
        cra = Runner.crawl(Scrapy_ModuleSpider,self.categoryList)
        cra.addBoth(lambda _: self.spider_closing(cra))
        #开始爬取
        self.logger.info("Run reactor")
        reactor.run()

    def run(self):
        self.crawl(Reference_Data.categoryList)


if __name__ == '__main__' :
    Scrapy_Module = Scrapy_Module()
    if len(sys.argv) == 1:
        Scrapy_Module.crawl(Reference_Data.categoryList)
    else:
        for para in sys.argv:
            if para == 'reset':
                Scrapy_Module.logger.info("Reset Database person.")
                Database = PersonDatabase()
                Database.dropDatabase('person')
                Database.close()
                commands.getstatusoutput('rm *~')
                commands.getstatusoutput('rm Scrapy_Project/*~')
                commands.getstatusoutput('rm Scrapy_Project/spiders/*~')
                commands.getstatusoutput('rm *pyc')
                commands.getstatusoutput('rm Scrapy_Project/*pyc')
                commands.getstatusoutput('rm Scrapy_Project/spiders/*pyc')
                commands.getstatusoutput('rm -r Scrapy_Project/result/')
            elif para == 'export':
                Database = PersonDatabase()
                Scrapy_Module.logger.info("Export xls File ")
                Database.exportToXls()
                Scrapy_Module.logger.info("Export sql File ")
                Database.exportToSql()
                Database.close()
            elif para == 'tar':
                Scrapy_Module.logger.info("Tar to ../../person_hudongbaike.tar")
                commands.getstatusoutput('tar -cvf ../../person_hudongbaike.tar ../../person_hudongbaike/')


    




