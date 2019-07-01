from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import URLError
import pymysql
import asyncio
import aiomysql
from urllib.parse import quote
import string

loop = asyncio.get_event_loop()

@asyncio.coroutine
def connectMysql():
    conn = yield from aiomysql.connect(host="127.0.0.1", port=3306,
                                user='root', password='', 
                                db='chiayitravel', charset='utf8', autocommit=True)
    cursor = yield from conn.cursor()
    yield from cursor.execute("select name from shop")
    selectResult = yield from cursor.fetchall()
    #for record in result:
    #    print(record)
    yield from cursor.close()
    conn.close()
    return selectResult

@asyncio.coroutine
def insertData(values):
    conn = yield from aiomysql.connect(host="127.0.0.1", port=3306,
                                user='root', password='', 
                                db='chiayitravel', charset='utf8', autocommit=True)
    cursor = yield from conn.cursor()
    #print(values)
    #sql = 'INSERT INTO pixcrawl VALUES(%s,%s,%s,%s)'
    yield from cursor.executemany('INSERT INTO pixcrawl VALUES(%s,%s,%s,%s)', values)
    conn.close()

def tryRequestError(url):
    try:
        url
    except HTTPError as e:
        return False
    except URLError as e:
        return False
    return True

def main():
    getName = loop.run_until_complete(connectMysql())
    for index in range(len(getName)):
        #print(getName[index][0])
        url = 'https://www.pixnet.net/searcharticle?q=%s&page=1'%quote(getName[index][0],safe=string.printable)
        print(url)
        html = urlopen(url)
        #html = urlopen('https://www.pixnet.net/searcharticle?q=%s&page=1'%quote('PANdora263.ART%20潘朵拉工作室'))
        if html:
            row = list()
            titleList = list()
            clickList = list()
            releaseList = list()
            urlList = list()

            bs = BeautifulSoup(html.read(), 'html.parser')
            infoList = bs.find_all('ul', {'class':'search-text'})
            linkList = bs.find_all('li', {'class':'search-title'})

            for info in infoList:
                titleList.append(info.find('a').attrs['title'])
                clickList.append(info.find('span',{'class':'search-views'}).get_text())
                releaseList.append(info.find('span',{'class':'search-postTime'}).get_text())
                
                #print(info.find('a').attrs['title'])                                #文章標題
                #print(info.find('span',{'class':'search-views'}).get_text())        #人氣
                #print(info.find('span',{'class':'search-postTime'}).get_text())     #發表時間
                
                
            for link in linkList:
                urlList.append(link.find('a').attrs['href'])
                #print(link.find('a').attrs['href'])                                 #文章url


            for i in range(len(titleList)):
                data = list()
                data.append(titleList[i])
                data.append(clickList[i])
                data.append(releaseList[i])
                data.append(urlList[i])
                row.append(tuple(data))

            #print(row)
        
            #loop.run_until_complete(insertData(row))
        else:
            print('The server could not be found!')
    print(html)


if __name__=="__main__":
    main()
