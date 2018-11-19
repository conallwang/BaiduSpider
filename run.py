from utils.IndexPages import IndexPage
from multiprocessing import Process
from multiprocessing import Pool
from utils.IndexPages import get_last_line
import re
from utils.DetailedPages import DetailedPages
import os
from utils.args import *


def One_Process(keyword, logNum):
    i = IndexPage(keyword)
    totalPages = int(i.get_totalPages())
    filename = './log/log' + str(logNum) + '.txt'
    lastLine = get_last_line(filename)
    if lastLine:
        lastLine = str(lastLine, encoding='gbk')
        pattern = re.compile(r'完成第(\d+)个索引')
        currentIndexPage = int(re.search(pattern, lastLine).group(1))
        pattern = re.compile(r'索引页面中的第(\d+)个详情')
        currentParentPage = int(re.search(pattern, lastLine).group(1))
        page = currentIndexPage - 1
        count = currentParentPage + 1
        urlList = i.main(page * 50)
        if urlList:
            L = len(urlList) - currentParentPage
            urlList = urlList[-L:]
            for url in urlList:
                d = DetailedPages(url, page + 1, count, filename)
                d.main()
                count += 1
    else:
        currentIndexPage = 0

    for page in range(currentIndexPage, totalPages):
        count = 1
        urlList = i.main(page*50)
        if urlList:
            for url in urlList:
                d = DetailedPages(url, page+1, count, filename)
                d.main()
                count += 1


def main():
    print('开始爬取指定的贴吧...')
    id = 18     # 修改此可爬取list对应的id之后的关键词
    for item in TIEBA[id:]:
        p = Process(target=One_Process, args=(item, id))
        p.start()
        id += 1
    p.join()
    print('所有子进程爬取完成.')


if __name__ == '__main__':
    main()
