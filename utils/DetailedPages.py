
from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException
import re
from urllib.parse import urlencode
from utils.config import *
import pymongo
import datetime

class DetailedPages(object):
    def __init__(self, url, indexPage, parentPage, filename):
        self.url = url
        self.indexPage = indexPage
        self.parentPage = parentPage
        self.filename = filename


    def get_totalPages(self, url):
        html = self.get_pages(url)
        # print(html)
        pattern = re.compile(r'<span class="red">(\d+)</span>页')
        totalPages = re.search(pattern, str(html))
        if totalPages:
            totalPages = totalPages.group(1)
            return int(totalPages)
        return None


    def save_to_MongoDB(self, result):
        """
        存储到MongoDB
        :param result: 待存储数据
        :return: 是否存储成功
        """
        client = pymongo.MongoClient(MONGO_URL)
        db = client[MONGO_DB]
        try:
            # if not db[MONGO_TABLE].update({'content': result['content']}, result, True)['updatedExisting']:
            if db[MONGO_TABLE].insert(result):
                print('成功存储到MongoDB: ' + str(result))
                return True
            print('已经重复,插入失败.')
            return False
        except Exception as e:
            print(e)
            return False


    def parse_detailed_page(self, html):
        soup = BeautifulSoup(html, 'lxml')
        content = soup.find_all('div', {'class': 'j_d_post_content'})
        if content:
            for item in content:
                pattern = re.compile(r'([0-9]*[\u4e00-\u9fa5]+)+', re.S)
                if not item.string:
                    text = re.findall(pattern, str(item))
                    for t in text:
                        result = {
                            'content': t
                        }
                        self.save_to_MongoDB(result)
                else:
                    result = {
                        'content': item.string
                    }
                    self.save_to_MongoDB(result)


    def get_pages(self, url):
        try:
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                response.encoding='utf-8'
                return response.text
            print('无法正常请求详情页.' + str(response.status_code))
            return None
        except RequestException as e:
            print(e.args)
            return None


    def main(self):
        data = {
            'pn': '1'
        }
        url = self.url + '?' + urlencode(data)
        print(url)
        totalPages = self.get_totalPages(url)
        html = self.get_pages(url)
        if html:
            self.parse_detailed_page(html)
        with open(self.filename, 'a') as f:
            f.write('当前爬取完成第' + str(self.indexPage) + '个索引页面'
                    + '中的第' + str(self.parentPage) + '个详情页面'
                    + '中的第1页' + '--------'
                    + str(datetime.datetime.now()) + '\n')
            f.close()
        if totalPages:
            if totalPages >= 2:
                for page in range(2, totalPages + 1):
                    data = {
                        'pn': page
                    }
                    url = self.url + '?' + urlencode(data)
                    print(url)
                    html = self.get_pages(url)
                    if html:
                        self.parse_detailed_page(html)
                    with open(self.filename, 'a') as f:
                        f.write('当前爬取完成第' + str(self.indexPage) + '个索引页面'
                                + '中的第' + str(self.parentPage) + '个详情页面'
                                + '中的第' + str(page) + '页' + '--------'
                                + str(datetime.datetime.now()) + '\n')
                        f.close()
