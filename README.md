# 爬取豆瓣读书
爬取豆瓣读书下任意标签的所有图书，然后保存在数据库中！
在爬取的过程中，可能会遇到一本书，有几个标签，所以就会遇到重复的问题!
我用MySQL数据进行去重，插入数据前，判断数据库中是否已经存在数据了！

豆瓣读书所有标签
![豆瓣读书的标签](https://github.com/JXiuFen/-/blob/master/%E8%B1%86%E7%93%A3%E8%AF%BB%E4%B9%A6%E6%A0%87%E7%AD%BE.png?raw=true)

标签下的图书
![所有的图书](https://github.com/JXiuFen/-/blob/master/%E8%B1%86%E7%93%A3%E8%AF%BB%E4%B9%A6%E5%9B%BE%E4%B9%A6.png?raw=true)



程序运行后，手动输入你要爬取的图书标签
![程序运行](https://github.com/JXiuFen/-/blob/master/%E4%BB%A3%E7%A0%81%E8%BF%90%E8%A1%8C.png?raw=true)


程序运行中，在爬取指定的标签下的所有图书
![爬取中](https://github.com/JXiuFen/-/blob/master/%E7%88%AC%E5%8F%96%E4%B8%AD.png?raw=true)



把爬取到的数据，保存到MySQL数据库中
![保存数据](https://github.com/JXiuFen/-/blob/master/%E6%95%B0%E6%8D%AE%E4%BF%9D%E5%AD%98.png?raw=true)
