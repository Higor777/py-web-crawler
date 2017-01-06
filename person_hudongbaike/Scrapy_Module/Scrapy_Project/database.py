# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')


import MySQLdb
import xlwt  

import Reference_Data
from collections import OrderedDict
import Reference_Data
import logging 

import commands

class PersonDatabase(object):
    connect = None
    cursor = None
    infoKeyMap = None
    connected = False
    logger = None
    sqlFileName = None
    xlsFileDir = None
    def __init__(self):
        self.logger = logging.getLogger('Scrapy_Module') # 获取名为Scrapy_Module的logger 
        self.infoKeyMap = OrderedDict(Reference_Data.infoKeyMapList)
        self.connect()
        self.usePerson()
        if self.connected :
            tables = self.getAllTables()
            for category in Reference_Data.categoryDict.values() :
                if category not in tables:
                    self.createTable(category)
        result_dir = os.path.split(os.path.realpath(__file__))[0] + '/result/'
        self.sqlFileDir = result_dir + 'sql/'
        self.xlsFileDir = result_dir + 'personInfoXls/'
        if not os.path.exists(result_dir):
            os.mkdir(result_dir)
        if not os.path.exists(self.sqlFileDir):
            os.mkdir(self.sqlFileDir)
        if not os.path.exists(self.xlsFileDir):
            os.mkdir(self.xlsFileDir)

    def connect(self):
        try:
            self.connect= MySQLdb.connect(
                host='localhost',
                user='root',
                passwd='higor1234567.',
                #db ='person',
                charset = 'utf8'
                )
            self.connected = True
            self.cursor = self.connect.cursor()
        except Exception,e:
            self.logger.error("ERROR:Database connect failed.")
            self.logger.error(e)

    def usePerson(self):
        try:
            if 'person' not in self.getAllDatabases():
                self.createDatabase('person')
            self.cursor.execute('use person')
            self.cursor.execute('set names utf8')
        except Exception,e:
            self.logger.error("ERROR:Create Database person failed.")
            self.logger.error(e)

    def useCategory(self):
        try:
            if 'category' not in self.getAllDatabases():
                self.createDatabase('category')
            self.cursor.execute('use category')
            self.cursor.execute('set names utf8')
        except Exception,e:
            self.logger.error("ERROR:Create Database category failed.")
            self.logger.error(e)
        try:
            if 'categoryTable' not in self.getAllTables():
                self.cursor.execute('create table categoryTable (category varchar(50) primary key,subCategory text)')
        except Exception,e:
            self.logger.error("ERROR:Create Table categoryTable failed.")
            self.logger.error(e)

    def insertCategory(self,SubCategoryList):
        if self.connected :
            for Category in SubCategoryList.keys():
                if SubCategoryList[Category]:
                    try:
                        self.cursor.execute('insert into categoryTable values(\'' + Category + '\',\'' + SubCategoryList[Category] + '\')')
                        self.connect.commit()
                    except Exception,e:
                        self.connect.rollback()
                        self.logger.error("ERROR:Database insert failed.")
                        self.logger.error(e)

    def createDatabase(self,Database):
        if self.connected :
            if Database not in self.getAllDatabases():
                self.logger.info('create database ... ' + Database)
                self.cursor.execute('create database ' + Database + ' DEFAULT CHARSET utf8 COLLATE utf8_general_ci')
            else:
                self.logger.error('Database ' + Database + ' has existed.')   

    def dropDatabase(self,Database):
        if self.connected :
            if Database in self.getAllDatabases():
                self.logger.info('drop database ... ' + Database)
                self.cursor.execute('drop database ' + Database)
            else:
                self.logger.error('Database ' + Database + ' not existed.')     

    def createTable(self,tablename):
        if self.connected :
            sql = 'create table ' + tablename + '('
            for key in self.infoKeyMap.values():
                if key in Reference_Data.dataBaseKey:
                    sql = sql + key + ' varchar(20),'
                elif key in ['nationality','people','education']:
                    sql = sql + key + ' varchar(15),'
                elif key in ['marriage']:
                    sql = sql + key + ' varchar(7),'
                elif key in ['gender','blood']:
                    sql = sql + key + ' varchar(5),'
                elif key in ['height','weight']:
                    sql = sql + key + ' int,'
                else:
                    sql = sql + key +' text,'
            sql = sql + 'cururl text,'
            sql = sql + 'primary key ('
            for key in Reference_Data.dataBaseKey:
                sql = sql + key + ','
            sql = sql[0:-1]
            sql = sql + '))'  
            sql = sql.encode('utf-8')
            #print sql
            self.cursor.execute(sql)

    def dropTable(self,table):
        if self.connected :
            if table in self.getAllTables():
                self.logger.info('drop database ... ' + table)
                self.cursor.execute('drop table ' + table)
            else:
                self.logger.error('Table' + table + 'not existed.')                

    def insert(self,item):
        if self.connected :
            for itemCategory in item['category']:
                sql = 'insert into ' + Reference_Data.categoryDict[itemCategory] + '('
                values = ') values('
                for key in item.keys():
                    if key != 'category':
                        sql = sql + key + ','
                        if key in ['height','weight']:
                            values = values + item[key] + ','
                        else:
                            values = values + '\'' + item[key] + '\','
                sql = sql[0:-1] + values[0:-1] +  ')'
                sql = sql.encode('utf-8')
                #print sql
                try:
                    self.cursor.execute(sql)
                    self.connect.commit()
                except Exception,e:
                    self.connect.rollback()
                    self.logger.error("ERROR:Database insert failed.")
                    self.logger.error(e)

    def getAllDatabases(self):
        if self.connected :
            count = self.cursor.execute('show databases')
            Databaseslist = []
            for i in self.cursor.fetchmany(count):
                Databaseslist.append(i[0])
            return Databaseslist

    def getAllTables(self):
        if self.connected :
            count = self.cursor.execute('show tables')
            tablelist = []
            for i in self.cursor.fetchmany(count):
                tablelist.append(i[0])
            return tablelist

    def dropAllTables(self):
        if self.connected :
            for table in self.getAllTables():
                self.dropTable(table)

    def showDatabaseInfo(self):
        if self.connected :
            for table in self.getAllTables():
                count = self.cursor.execute('select * from ' + table)  
                print table + ' has %s record' % count  

    def exportToXls(self):
        if self.connected :
            for table in self.getAllTables():
                count = self.cursor.execute('select * from ' + table)  
                print table + ' has %s record' % count  
                if count > 0 :
                    #重置游标位置  
                    self.cursor.scroll(0,mode='absolute')  
                    #搜取所有结果  
                    results = self.cursor.fetchall()  
                    #测试代码，print results  
                    #获取MYSQL里的数据字段  
                    fields = self.cursor.description  
                    #将字段写入到EXCEL新表的第一行  
                    wbk = xlwt.Workbook(encoding = 'utf-8')  
                    sheet = wbk.add_sheet(table,cell_overwrite_ok=True)  
                    style = xlwt.XFStyle()
                    font = xlwt.Font()
                    font.name = 'SimSun' # 指定“宋体”
                    style.font = font 
                    for ifs in range(0,len(fields)):  
                        sheet.write(0,ifs,fields[ifs][0])  
                    ics=1  
                    jcs=0  
                    for ics in range(1,len(results)+1):  
                        for jcs in range(0,len(fields)):  
                            sheet.write(ics,jcs,results[ics-1][jcs])  
                    wbk.save(self.xlsFileDir + table + '.xls')

    def exportToSql(self):
        cmd = 'mysqldump -h localhost -uroot -phigor1234567. --extended-insert=false person>' + self.sqlFileDir + 'personMySQL.sql'
        commands.getstatusoutput(cmd)
        with open(self.sqlFileDir + 'personMySQL.sql','r') as sqlfile:
            line = sqlfile.readline()
            SQLServerString = ''
            while line:
                if 'IF EXISTS' not in line and 'LOCK' not in line:
                    SQLServerString = SQLServerString + line
                line = sqlfile.readline()
        SQLServerString = SQLServerString.replace('ENGINE=InnoDB DEFAULT CHARSET=utf8','')
        SQLServerString = SQLServerString.replace('`','')
        SQLServerString = SQLServerString.replace('int(11)','int')
        with open(self.sqlFileDir + 'personSQLServer.sql','w') as sqlserverfile:
            sqlserverfile.write(SQLServerString)

    def close(self):
        if self.connected :
            self.cursor.close()
            self.connect.close()

if __name__ == '__main__' :
    Database = PersonDatabase()
    Database.exportToXls()
    Database.exportToSql()
    #Database.dropAllTables()
    Database.close()



    
