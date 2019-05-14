# -*- coding: utf-8 -*-
import requests, sys
import urllib
from bs4 import BeautifulSoup
from openpyxl import Workbook
import re
import time
key_words = [[r'一居室', r'独', r'一室户'], [r'成山', r'儿童医学中心', r'临沂', r'人民广场', r'人广', r'锦绣', r'老西门', r'耀华', r'东明']]
#key_words = [[r'蓝村', r'浦电', r'人民广场', r'人广', r'锦绣', r'龙阳', r'芳华', r'耀华', r'一居室']]
out_file = "d:/tmp/test.xlsx"
if len(sys.argv) == 2:
    out_file = "d:/tmp/{}.xlsx".format(str(sys.argv[1]))
    

#open excel
wb = Workbook()
ws = wb.active



"""
Parameters:
    无
Returns:
    无
Modify:
    2017-09-13
"""
class downloader(object):
    start_point = 0
    def __init__(self):
        self.server = 'https://www.douban.com/'
        self.target = 'http://www.douban.com/group/shanghaizufang/discussion?start={}'.format(downloader.start_point)
        self.names = []            #titles
        self.urls = []            #ursl
        self.users = []            #authors

    def filter_title(self, title):
        print(title)
        is_pass = True;
        for level in key_words:
            pass_level = False
            for key in level:
                if re.search(key, title):
                   pass_level = True
                   break
            if not pass_level:
                is_pass = False
                break
        return is_pass
    

    def get_download_url(self):
        try:
            #r = urllib.urlopen(self.target)
            req = requests.get(url = self.target)
        except:
            print("cann not open url {}".format(self.target))
            return 0
        html = req.text
        
        if not html: return
        soup = BeautifulSoup(html, features="html.parser",
                             from_encoding="utf-8")
        #soup = BeautifulSoup(r.read)
        #r.close()
        data = []
        
        #table = soup.find('table', attrs={'class':'olt'})
        table_body = soup.find('table', class_='olt')
        if table_body is None:
            print("cannot find table")
            return
        rows = table_body.find_all('tr')

        total_num = 0
        print(len(rows))
        for row in rows:
            if not row : continue
            try:
                cols = row.find_all('td')
                col0 = cols[0]
                a = col0.find('a')
                if not a: continue
                title = str(a.get('title'))
                # filter title with key_words
                is_match = self.filter_title(title)
                if not is_match: continue
                url = a.get('href')
                col1 = cols[1]
                a = col1.find('a')
                user = a.text
                ws.append([title, user, url])
                total_num += 1
            except:
                continue

        print("starting point: {}, get {}".format(downloader.start_point, total_num))

        
        
    """
    函数说明:获取章节内容
    Parameters:
        target - 下载连接(string)
    Returns:
        texts - 章节内容(string)
    Modify:
        2017-09-13
    """
    def get_contents(self, target):
        req = requests.get(url = target)
        html = req.text
        bf = BeautifulSoup(html)
        texts = bf.find_all('div', class_ = 'showtxt')
        texts = texts[0].text.replace('\xa0'*8,'\n\n')
        return texts

#reload(sys)
#sys.setdefaultencoding('utf-8')

dl = downloader()

for i in range(1, 120):
    downloader.start_point = 0
    dl.get_download_url()
    downloader.start_point = 25
    time.sleep(5)
    dl.get_download_url()
    downloader.start_point = 50
    time.sleep(5)
    dl.get_download_url()
    downloader.start_point = 75
    time.sleep(5)
    dl.get_download_url()
    time.sleep(180)


wb.save(out_file)
