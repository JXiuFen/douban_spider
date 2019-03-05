import requests
import headers
from  lxml import  etree
import re
import time
import pymysql


#获取所有标签
def one():
    url="https://book.douban.com/tag/?view=type&icn=index-sorttags-all"
    response=requests.get(url,headers=headers.headers).text
    html=etree.HTML(response)
    for i in range(6):
        title=html.xpath("//*[@id='content']/div/div[1]/div[2]/div[{}]/a/h2/text()".format(i+1))
        tag=html.xpath("//*[@id='content']/div/div[1]/div[2]/div[{}]/table/tbody/tr/td/a/text()".format(i+1))
        print(title[0])
        for j in tag:
            print(j,end=",")
        print("\n===================================================")

#爬取指定标签下的所有书籍
def two():
    one()
    tag=input("请输入要爬取得标签:")
    page=0
    while True:
          number=1        #书本数
          page=page*10    #页数
          url="https://book.douban.com/tag/{}?start={}&type=T".format(tag,page)       #构建页数的url
          print(url)
          response=requests.get(url,headers=headers.headers).text
          re_judge_tag=re.compile("豆瓣上暂时还没有人给书标注")
          if  re.findall(re_judge_tag,response):       #判断是否有此标签的书籍
              print("发现没有此标签！")
              tag=input("请重新输入要爬取得标签:")
              print("----------------")
              continue
            
          else:
              print("标签有效！\n")
              
          print("正在爬取{}页".format(int(page/10+1)))
          print("<"*30)
          html=etree.HTML(response)
          href_list=html.xpath("//ul[@class='subject-list']/li/div[@class='info']/h2/a/@href")          
          if href_list:
                for i in href_list:
                      print("第{}本书".format(number))
                      
                      response_1=requests.get(i,headers=headers.headers).text
                      html_1=etree.HTML(response_1)
                      book_name=html_1.xpath("//div[@id='wrapper']/h1/span/text()")
                      author=html_1.xpath("//div[@id='info']/a[1]/text()")
                      re_press=re.compile(r'<span class="pl">出版社:</span> (.+)<br/>')
                      re_published = re.compile(r'<span class="pl">出版年:</span> (.+)<br/>')
                      re_number_page = re.compile(r'<span class="pl">页数:</span> (.+)<br/>')
                      re_original_book_name = re.compile(r'<span class="pl">原作名:</span> (.+)<br/>')
                      re_pricing=re.compile(r'<span class="pl">定价:</span> (.+)<br/>')
                      score=html_1.xpath("//div[@class='rating_self clearfix']/strong[@class='ll rating_num ']/text()")
                      comments=html_1.xpath("//div[@class='rating_sum']/span/a/span/text()")
                      img_src=html_1.xpath("//a[@class='nbg']/img/@src")
                      
                      if author:                         #判断《作者》是否存在    
                          author=author[0].strip("\n ")
                          
                      else:
                          author=html_1.xpath("//div[@id='info']/span[1]/a/text()")
                          
                          if author!=" ":
                              author="无"
                          author=author[0].strip("\n ")
                      if re.findall(re_press,response_1) :   #判断《出版社》是否存在
                          press=re.findall(re_press,response_1)

                      else:
                          press="无"
                          
                      if re.findall(re_number_page, response_1):   #判断《页数》是否存在
                          number_page = re.findall(re_number_page, response_1)
                      else:
                          number_page="无"
                          
                      if re.findall(re_original_book_name,response_1):   #判断《原书名》是否存在
                          original_book_name=re.findall(re_original_book_name,response_1)

                      else:
                          original_book_name="无"

                      if comments:             #判断《评论人数》是否存在
                          pass

                      else:
                          comments = "无"

                      if re.findall(re_published, response_1):
                          published = re.findall(re_published, response_1)      #判断《出版年》是否存在
                      else:
                          published = "无"

                      if re.findall(re_pricing,response_1):                 #判断《定价》是否存在
                          pricing=re.findall(re_pricing,response_1)
                      else:
                          pricing="无"
                          
                      
                      print("书名：",book_name[0])
                      print("作者：",author)
                      print("出版社:",press[0])
                      print("出版年：",published[0])
                      print("页数：",number_page[0])
                      print("定价:",pricing[0])
                      print("评分：",score[0])
                      print("评论人数：",comments[0])
                      print("原书名：",original_book_name[0])
                      print("书封面的url:",img_src[0])
                      print("*"*30)
                      
                      number+=1  #书本数自加
                      save_mysql(book_name[0],author,press[0],published[0],number_page[0],pricing[0],score[0],comments[0],original_book_name[0],img_src[0])
                      time.sleep(2)
          else:
                print("已经没有书可爬了！")
                break
          page=int(page/10+1)


#将数据保存到mysql数据中
def save_mysql(book_name,author,press,published,number_page,pricing,score,comments,original_book_name,img_src):
        # 连接MySQL数据库
        db = pymysql.connect("192.168.111.131", "root", "123456", "pymsql")
        # 获取游标
        cursor = db.cursor()

        # 写入数据
        #insert_sql = """INSERT INTO douban_book_foreign_literature (书名,作者,出版社,出版年,页数,定价,评分,评论人数,原书名,书封面的url)VALUES (%s, %s, %s, %s,%s,%s,%s,%s,%s,%s)"""

        #判断数据库中是否已经有这条数据啦，如果有则忽略，如果没有则插入数据
        insert_sql=""" INSERT INTO douban_book_foreign_literature(书名,作者,出版社,出版年,页数,定价,评分,评论人数,原书名,书封面的url) SELECT %s, %s, %s, %s,%s,%s,%s,%s,%s,%s FROM DUAL WHERE NOT EXISTS(SELECT * FROM douban_book_foreign_literature WHERE 书名 = %s)"""
        try:

            # 执行sql语句
            cursor.execute(insert_sql,(book_name,author,press,published,number_page,pricing,score,comments,original_book_name,img_src,book_name))
            # 提交到数据库执行
            db.commit()
            print("写入数据库成功！")
            print("*"*30)
        except Exception as e:
            # 如果发生错误则回滚
            db.rollback()
            print(e)
            print("写入数据库失败！")
        # 关闭数据库连接
        db.close()

if  __name__=='__main__':
    two()
    
