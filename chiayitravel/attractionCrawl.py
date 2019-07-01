from selenium import webdriver
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
                                db='chiayitravel', charset='utf8mb4', autocommit=True)
    cursor = yield from conn.cursor()
    yield from cursor.execute("select name, attrId from attraction")
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
    yield from cursor.executemany('INSERT INTO pixcrawl(title, click_of_times, release_time, url, storeId) VALUES(%s,%s,%s,%s,%s)', values)

def main():
    getData = loop.run_until_complete(connectMysql())
    for index in range(len(getData)):

        print(getData[index][0])
        #url = 'https://www.pixnet.net/tags/'%quote(getData[index][0],safe=string.printable)
        url = 'https://www.pixnet.net/tags/' + quote(getData[index][0],safe=string.printable)
        print(url)
        attrId = getData[index][1]

        driver = webdriver.Chrome()
        driver.get(url)
        content_element = driver.find_element_by_class_name('sc-1ir7rbw-0')
        content_html = content_element.get_attribute('innerHTML')

        #html = urlopen(url)
        if content_html:
            row = list()
            titleList = list()
            clickList = list()
            releaseList = list()
            urlList = list()

            bs = BeautifulSoup(content_html, 'html.parser')
            infoList = bs.find_all('section',{'class':'sc-1ckrxmq-0'})
            for info in infoList:
                #print(info.find('p',{'class':'sc-15yfh73-8 fQudZ'}).get_text())
                titleList.append(info.find('h2',{'class':'sc-1hu2j4t-2'}).get_text())
                releaseList.append(info.find('p',{'class':'sc-15yfh73-8'}).get_text())
                urlList.append(info.find('a', {'class':'sc-1hu2j4t-0'}).attrs['href'])
                
                isTwoClick = info.find_all('a',{'class':'wbmo2y-1'})
                if(len(isTwoClick)>1): #如果今天有footer有留言，那人氣就在後面
                    clickList.append(isTwoClick[1].string)
                elif len(isTwoClick)==1:                   #如果今天有footer沒有留言，那人氣就在前面
                    clickList.append(isTwoClick[0].string)
                else:
                    clickList.append('無')

                print('文章時間:')
                print(info.find('p',{'class':'sc-15yfh73-8'}).get_text())#文章時間
                print('文章url:')
                print(info.find('a', {'class':'sc-1hu2j4t-0'}).attrs['href'])#文章url
                print('文章標題:')
                print(info.find('h2',{'class':'sc-1hu2j4t-2'}).get_text())#文章標題
                print('文章點擊次數:')
                click_of_times = info.find_all('a',{'class':'wbmo2y-1'})
                #print(click_of_times[0])
                if(len(click_of_times)>1):
                    print(click_of_times[1].string)#文章點擊次數
                elif len(click_of_times)>1:
                    print(click_of_times[0].string)#文章點擊次數
                else:
                    print("無")
                print(attrId)  
                print()
            
            for i in range(len(titleList)):
                dataTuple = list()
                dataTuple.append(titleList[i])
                dataTuple.append(clickList[i])
                dataTuple.append(releaseList[i])
                dataTuple.append(urlList[i])
                dataTuple.append(attrId)
                row.append(tuple(dataTuple))
            
            driver.close()
            loop.run_until_complete(insertData(row))
        else:
            print('The server could not be found!')
            

if __name__=="__main__":
    main()
