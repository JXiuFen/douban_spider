import re
import time
import pymysql
import requests
from numpy import random
from  lxml import etree
import smtplib
from email.mime.text import MIMEText

# python douban_book_spider.py args1 | tee -a douban_log.txt

# create database books
# use books
# create table douban_books (id int unsigned auto_increment, category_name varchar(30), book_name varchar(300), author varchar(300), score varchar(20), comments varchar(20), primary key(id))

USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]

# change for yourself
mysql_host = "127.0.0.1"
mysql_port = 3306
mysql_user = "root"
mysql_password = "123456"
mysql_database = "books"

# get available ip and construct proxy
def get_headers():
    return {'User-Agent': USER_AGENTS[random.randint(0, len(USER_AGENTS)-1)], 'Connection': 'close'}

def get_category_list():
    category_tags = []
    url="https://book.douban.com/tag/?view=type&icn=index-sorttags-all"
    response = requests.get(url, headers=get_headers(), proxies=proxies).text
    html = etree.HTML(response)
    for i in range(6):
        tags = html.xpath("//*[@id='content']/div/div[1]/div[2]/div[{}]/table/tbody/tr/td/a/text()".format(i+1))
        for j in tags:
            category_tags.append(j)
    return category_tags

def get_each_book_info(tag):
    page = 1
    while True:   
        url = "https://book.douban.com/tag/{}?start={}&type=S".format(tag, (page - 1) * 20)       
        print(url)
        response = requests.get(url, headers=get_headers(), proxies=proxies).text
        print("正在爬取{}页".format(page))
        print("<" * 30)
        html = etree.HTML(response)
        book_info = html.xpath("//ul[@class='subject-list']/li/div[@class='info']")
        if book_info == []:
            break
        pattern = re.compile(r'\d+\.?\d*')
        for item in book_info:
            book_basic_raw = item.xpath("./div[@class='pub']/text()")
            book_comments_raw = item.xpath("./div[2]/span[@class='pl']/text()")
            book_score_raw = item.xpath("./div[2]/span[@class='rating_nums']/text()")
            book_name_raw = item.xpath("./h2/a/@title")
            try:
                book_basic_list = [item.strip() if item != None else "" for item in book_basic_raw[0].split(" / ") ]
                book_press = book_basic_list[len(book_basic_list) - 3]
                book_price = book_basic_list[len(book_basic_list) - 1]
                book_date = book_basic_list[len(book_basic_list) - 2]
                book_author = "/".join(book_basic_list[:len(book_basic_list) - 3])
            except:
                book_press = "无"
                book_price = "无"
                book_date = "无"
                book_author = "无"
            try:
                book_comments = pattern.findall(book_comments_raw[0])[0]
            except:
                book_comments = str(0)
            try:
                book_score = book_score_raw[0]
            except:
                book_score = str(0)
            try:
                book_name = book_name_raw
            except:
                book_name = ""
            print(book_name, book_author, book_date, book_price, book_press, book_score, book_comments)
            save_mysql(tag, book_name, book_author, book_score, book_comments)
        page += 1
        time.sleep(random.rand())

#将数据保存到mysql数据中
def save_mysql(category_name, book_name, author, score, comments):
    db = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_password, db=mysql_database)
    cursor = db.cursor()
    insert_sql = """ INSERT INTO douban_books(category_name, book_name, author, score, comments) SELECT %s, %s, %s, %s, %s"""
    try:
        cursor.execute(insert_sql, (category_name, book_name, author, score, comments))
        db.commit()
        print("写入数据库成功！")
        print("*" * 30)
    except Exception as e:
        db.rollback()
        print(e)
        print("写入数据库失败！")
    db.close()
if  __name__ == '__main__':
    try:
        category_list = get_category_list()
        for item in category_list:
            get_each_book_info(item)
    except Exception as why:
        print(why)
