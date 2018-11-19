
from utils.config import *
import requests
from requests import RequestException
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from utils.DetailedPages import DetailedPages
import os
import re


def get_last_line(inputfile):
    if not os.path.exists(inputfile):
        f = open(inputfile, 'a')
        f.close()
    filesize = os.path.getsize(inputfile)
    blocksize = 1024
    dat_file = open(inputfile, 'rb')
    last_line = ""
    if filesize > blocksize:
        maxseekpoint = (filesize // blocksize)
        dat_file.seek((maxseekpoint - 1) * blocksize)
    elif filesize:
        # maxseekpoint = blocksize % filesize
        dat_file.seek(0, 0)
    lines = dat_file.readlines()
    if lines:
        last_line = lines[-1].strip()
    # print "last line : ", last_line
    dat_file.close()
    return last_line


class IndexPage(object):
    def __init__(self, keyword):
        """
        构造函数
        :param keyword: 搜索贴吧的关键词
        """
        self.keyword = keyword


    def parse_index_page(self, html):
        """
        当前索引页中的所有url
        :param html: 索引页的html
        :return: 待访问的url
        """
        soup = BeautifulSoup(html, 'lxml')
        all_href = soup.find_all('a', {'rel': 'noreferrer', 'class': 'j_th_tit'})
        urlList = []
        for item in all_href:
            urlList.append('https://tieba.baidu.com' + item['href'])
        return urlList


    def get_index_page(self, url):
        """
        还缺一个错误之后重新访问的东西
        :return: 相应贴吧首页的html
        """
        try:
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                return response.text
            print('无法正常请求网页.' + str(response.status_code))
            return None
        except RequestException as e:
            print(e.args)
            return None


    def get_totalPages(self):
        data = {
            'kw': self.keyword,
        }
        url = 'https://tieba.baidu.com/f?' + urlencode(data)
        html = self.get_index_page(url)
        if html:
            pattern = re.compile(r'<a href="//tieba.baidu.com/f\?.*?pn=(\d+)" class="last pagination-item " >尾页</a>')
            totalPages = re.search(pattern, html)
            if totalPages:
                return totalPages.group(1)


    def main(self, page):
        """
        执行和测试
        :return:
        """
        data = {
            'kw': self.keyword,
            'pn': page,
            'ie': 'utf-8'
        }
        url = 'https://tieba.baidu.com/f?' + urlencode(data)
        html = self.get_index_page(url)
        if html:
            return self.parse_index_page(html)


if __name__ == '__main__':
    i = IndexPage('李毅', 1)
    lastLine = str(get_last_line('./log.txt'), encoding='gbk')
    # print(lastLine)
    pattern = re.compile(r'完成第(\d+)个索引')
    currentIndexPage = int(re.search(pattern, lastLine).group(1))
    pattern = re.compile(r'索引页面中的第(\d+)个详情')
    currentParentPage = int(re.search(pattern, lastLine).group(1))
    page = currentIndexPage - 1
    count = currentParentPage + 1
    urlList = i.main(page * 50)
    # print(len(urlList))
    L = len(urlList) - currentParentPage
    # print(L)
    urlList = urlList[-L:]
    if urlList:
        for url in urlList:
            d = DetailedPages(url, page + 1, count)
            d.main()
            count += 1

    for page in range(currentIndexPage, 365208):
        count = 1
        urlList = i.main(page*50)
        if urlList:
            for url in urlList:
                d = DetailedPages(url, page+1, count)
                d.main()
                count += 1
