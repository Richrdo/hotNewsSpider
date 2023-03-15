import json
import requests
import pymysql
import time
from datetime import  datetime
from threading import Timer

# import BeautifulSoup as bs4
from lxml import etree

class SpNews:
    def __init__(self):
        self.url="https://news.china.com/";
        self.header={
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        }

     #爬取html
    def getHtml(self,url):
        htmlStr=requests.get(url).content;
        html=etree.HTML(htmlStr);
        return html;

    def saveToDB(self,news_title,news_date,news_content,theme,news_source):
        # 修改数据库配置
        db=pymysql.connect(host="localhost:3306",user= "user",port=3306,password="password",database="hot_news_db",charset="utf8");
        cursor=db.cursor();
        sql="select news_id from news where news_title=%s";
        cursor.execute(sql,news_title)
        results=cursor.rowcount;
        if results==1:
            print("该新闻已存在");
        else:
            sql="insert into news(`news_title`,`news_type`,`news_source`,`news_date`,`news_content`) values (%s,%s,%s,%s,%s)" ;
            cursor.execute(sql,(news_title,theme,news_source,news_date,news_content));
        db.commit();
        db.close();

    def saveNews(self,news_title,news_date,news_content,theme,news_source):
        file=open(theme+"/"+news_date.split(" ")[0]+".json","a+",encoding="utf-8");
        news_json={
            "news_title":news_title,
            "news_date":news_date,
            "news_source":news_source,
            "news_content":news_content
        }
        str=json.dumps(news_json);
        file.write(str);
        file.close();

    #获取一条新闻并保存
    def getNews(self,url,theme):
        html=self.getHtml(url);
        # 获取新闻标题和时间
        news_title=html.xpath("//h1[@class='article_title']/text()")[0];
        news_date=html.xpath("//span[@class='time']/text()")[0];
        news_source_arg=html.xpath("//span[@class='source']/a/text()");
        news_source="中华网";
        print("来源长度", len(news_source_arg));
        if len(news_source_arg)==0:
            news_source=="无";
        else:
            news_source=news_source_arg[0];
        print("********************"+"正在获取新闻:"+news_title+"********************\n");
        print("新闻来源:"+news_source+"\n"+"theme:"+theme+"\n");
        # 获取新闻内容
        news_contents=html.xpath("//div[@class='article_content']//p/text()");
        news_content="\u3000\u3000";
        for str in news_contents:
            news_content=news_content+str+"\n\u3000\u3000";
            # news_content+=str;
        print("-------------------新闻内容是：" + "------------------\n" + news_content);
        self.saveToDB(news_title,news_date,news_content,theme,news_source);

    #爬取新闻
    def spXW(self,theme,url):
        print(theme);
        html=self.getHtml(url);
        news_url=html.xpath("//ul[@class='item_list mt0']/li/a/@href");
        for new_url in news_url:
            self.getNews(new_url,theme);

    #爬取不同模块的新闻
    def spMK(self):
        print("开始时间:",datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"\n");
        i=0;
        indexHtml=self.getHtml(self.url);
        themes_url=indexHtml.xpath("//div[@class='top_header_subnav']/a/@href");
        for i in {0,1,2}:
            self.spXW(themes_url[i].split("/")[-2],"https:"+themes_url[i]);

    def run(self):
        Timer(60*60,self.spMK).start();


if __name__=='__main__':
    mz=SpNews();
    mz.spMK();
    while True:
        mz.run();
        time.sleep(60*60);
