# -*- coding=utf-8 -*-
import urllib2
import threading
from Queue import Queue
import requests
from lxml import etree
import json


class Thread_Crawl(threading.Thread):
    def __init__(self, threadId, q):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.q = q

    def run(self):
        print "Starting " + self.threadId
        self.qiushiSpider()
        print "Exiting ", self.threadId

    def qiushiSpider(self):
        while True:
            if self.q.empty():
                break
            else:
                page = self.q.get()
                url = 'http://www.qiushibaike.com/8hr/page/' + str(page) + '/'
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
                    'Accept-Language': 'zh-CN,zh;q=0.8'
                }
                timeout = 4
                while timeout > 0:
                    timeout -= 1
                    try:
                        response = requests.get(url, headers=headers)
                        data_queue.put(response.text)
                        break
                    except Exception,e:
                        print e.message


class Thread_Parse(threading.Thread):
    def __init__(self, threadID, lock, queue, f):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.lock = lock
        self.queue = queue
        self.f = f

    def run(self):
        print 'starting ', self.threadID
        global exitFlag_Parse
        while not exitFlag_Parse:
            try:
                item = self.queue.get(False)
                if not item:
                    pass
                self.parse_data(item)
                self.queue.task_done()
            except:
                pass
        print 'Exiting ', self.threadID

    def parse_data(self, item):
        global total
        try:
            content = etree.HTML(item)
            result = content.xpath('//div[contains(@id,"qiushi_tag")]')
            for site in result:
                try:
                    imgUrl = site.xpath('./div/a/img/@src')[0]
                    title = site.xpath('.//h2')[0].text
                    content= site.xpath('.//div[@class="content"]/span')[0].text.strip()
                    vote = None
                    comments = None
                    try:
                        vote = site.xpath('.//div[@class="stats"]/span/i')[0].text
                        comments = site.xpath('.//a/i[@class="number"]')[0].text
                    except:
                        pass
                    result = {
                        'imgUrl': imgUrl,
                        'title': title,
                        'content': content,
                        'vote': vote,
                        'comments': comments,
                    }

                    with self.lock:
                        self.f.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
                except Exception:
                    pass
        except Exception:
            pass
        with self.lock:
            total += 1


data_queue = Queue()
lock = threading.Lock()
exitFlag_Parse = False
total = 0

def main():
    startpage = int(raw_input('请输入起始页：'))
    endPage = int(raw_input("请输入终止页："))

    output = open('qiushibaike.json', 'a')
    pageQuequ = Queue(50)
    for page in range(startpage, endPage):
        pageQuequ.put(page)

    crawlList=[]
    crawlThread = ['crawl_1', 'crawl_2', 'crawl_3']
    for crawlId in crawlThread:
        thread = Thread_Crawl(crawlId, pageQuequ)
        thread.start()
        crawlList.append(thread)

    parseThread = ['parse_1', 'parse_2', 'parse_3']
    for parseID in parseThread:
        thread_p = Thread_Parse(parseID, lock, data_queue, output)
        thread_p.start()
        parseThread.append(thread_p)

    while not pageQuequ.empty():
        pass

    for t in crawlList:
        t.join()

    while not data_queue:
        pass

    global exitFlag_Parse
    exitFlag_Parse = True

    with lock:
        output.close()

if __name__ == '__main__':
    main()