# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.split(os.path.realpath(__file__))[0] + '/../')


from database import PersonDatabase
import urllib
import requests
from urllib import unquote
from bs4 import BeautifulSoup
import commands

def GetUrlPool(categoryName):     
    #POST
    postdata = {
     '':categoryName,
      }
    categoryName = urllib.urlencode(postdata)[1:]
    postdata = {
     'categoryName':unquote(categoryName),
     'pagePerNum':1000,
     'pageNow':1,
      }
    r = requests.post('http://fenlei.baike.com/categorySpecialTopicAction.do?action=showDocInfo', data=postdata)
    urlpool = []
    for i in r.json()['list']:
        urlpool.append(i['title_url'])
    #print urlpool
    #print len(urlpool)
    return urlpool

count = 0
SubCategoryList = {}
recordCategoryList = []
#递归获取所有分类的直接子分类
def getDirectSubCategory(categoryName):
    global count
    global SubCategoryList
    global recordCategoryList
    if categoryName not in SubCategoryList.keys():
        SubCategoryList[categoryName] = []
    response = requests.get('http://fenlei.baike.com/' + categoryName)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text,'html.parser').find(class_ = 'sort_all up')
    if not soup:
        soup = BeautifulSoup(response.text,'html.parser').find(class_ = 'sort')
        if '下一级微百科' not in str(soup):
            soup = None
    if soup:
        soup = soup.p.find_next('p')
        if soup:
            Subsoup = BeautifulSoup(str(soup),'html.parser')
            Subsoup_a = Subsoup.a
            while Subsoup_a and Subsoup_a.text:
                categoryTemp = Subsoup_a.text
                if len(categoryTemp) >= 2:
                    for keyWord in ['手','家','人','员','师','将','王','明星','人物','皇后','总理','皇帝','总统','元帅']:
                        if len(keyWord) == 1:
                            if categoryTemp[-1] != keyWord:
                                continue
                        elif len(keyWord) == 2:
                            if categoryTemp[-2:] != keyWord:
                                continue
                        if categoryTemp not in SubCategoryList[categoryName]:
                            SubCategoryList[categoryName].append(categoryTemp)
                            count = count + 1
                            print categoryTemp,count
                            if categoryTemp not in recordCategoryList:
                                recordCategoryList.append(categoryTemp)
                                with open('可选人物分类列表.txt','a+') as file:
                                    file.write(categoryTemp + ' | ')
                                success = False
                                failCount = 0
                                while not success and failCount < 10:
                                    try:
                                        getDirectSubCategory(categoryTemp)
                                        success = True
                                    except Exception,e:
                                        failCount = failCount + 1
                                        print "ERROR: ",e
                        break
                Subsoup_a = Subsoup_a.find_next('a')


#递归合并所有子分类
def mergeDirectSubCategory(categoryName):
    global SubCategoryList
    for subCategory in SubCategoryList[categoryName]:
        if len(SubCategoryList[subCategory]) > 0:
            mergeDirectSubCategory(subCategory)
            for categoryTemp in SubCategoryList[subCategory]:
                if categoryTemp not in SubCategoryList[categoryName]:
                    SubCategoryList[categoryName].append(categoryTemp)

#获取某分类下的所有子分类
def getAllSubCategory(categoryName):
    global SubCategoryList
    Database = PersonDatabase()
    Database.useCategory()
    if Database.cursor.execute('select * from categoryTable') == 0:
        Database.close()
        print '数据库中无子分类信息，搜索生成中...'
        getDirectSubCategory('人物')
        '''
        try:
            for cateTemp in SubCategoryList.keys():
                mergeDirectSubCategory(cateTemp)
        except Exception,e:
            print e
        '''
        #将列表转换为字符串
        for relationKey in SubCategoryList.keys():
            string = ''
            for i in SubCategoryList[relationKey]:
                string = string + i + '/'
            string = string[0:-1]
            SubCategoryList[relationKey] = string
            #print relationKey + ' : ' + string
        Database = PersonDatabase()
        Database.useCategory()
        Database.insertCategory(SubCategoryList)
        print '导出子分类sql文件...'
        cmd = 'mysqldump -h localhost -uroot -phigor1234567.  category>categoryMySQL.sql'
        commands.getstatusoutput(cmd)
    count = Database.cursor.execute('select subCategory from categoryTable where category = \'' + categoryName + '\'')
    if count == 1:
        CategoryList =  Database.cursor.fetchone()[0].split('/')
    else :
        CategoryList = []
    Database.close()
    CategoryList.append(categoryName)
    string  = ''
    for category in CategoryList:
      string = string + category + ' '
    print string
    return CategoryList
 
if __name__ == '__main__' :
    try:
        #print GetUrlPool('政治人物')
        getAllSubCategory('人物')
    except Exception,e:
        print('Error:',e)
