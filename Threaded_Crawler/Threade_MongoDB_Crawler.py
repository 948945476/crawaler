#!/user/bin/env python
#-*- coding:utf-8 -*-
import urlparse
import re
import time
import threading
import os
import sys

from mongodbQueue import MongoQueue
sys.path.append(os.pardir)

try:
	from Public_Tools.downloader import Downloader
	from Public_Tools.Crawler_Tools import get_links, normalize, same_domain
except ImportError:
	print 'import package error:[place:{code:14 or 15}]'

SLEEP_TIME = 3
def Threaded_Crawler(seed_url, link_regex=None, delay=5, max_depth=-1, headers=None, user_agent='wswp', proxy=None, num_retries=1, cache=None,max_threads=5):
    '''利用MongoDB数据库存储的多线程爬虫'''
    #生成MongDB数据库存储link队列的实例
    crawl_queue = MongoQueue()
    #将基地址放入实例中
    crawl_queue.push(seed_url)
    D = Downloader(delay=delay, user_agent=user_agent, proxies=proxy, num_retries=num_retries, cache=cache)

    def process_queue():
    	#队列属性，如果能找出未标记为下载完毕的Url则为True
	    while crawl_queue:
	        try:
	        	url = crawl_queue.pop()
	        except KeyError:
	        	#当link存储队列发生异常时，说明没有url了，即可退出循环
	        	break
	        else:
	        	html = D(url)
	        	#将url标记为请求完成，但是请求结果是否正确不确定
	        	crawl_queue.complete(url)
	        	links = []
	        	if link_regex:
	        		links.extend(link for link in get_links(html) if re.match(link_regex, link))
	        		for link in links:
	        			link = normalize(seed_url, link)
	        			if same_domain(seed_url, link):
	        				crawl_queue.push(link)
    threads = []
    while threads or crawl_queue:
		for thread in threads:
			if not thread.is_alive():
				threads.remove(thread)
		while len(threads) < max_threads and crawl_queue:
			thread = threading.Thread(target=process_queue)
			thread.setDaemon(True)
			thread.start()
			threads.append(thread)
		time.sleep(SLEEP_TIME)