#!/user/bin/env python
#-*- coding:utf-8 -*-
import urlparse
import re
import time
import threading
import os
import sys
sys.path.append(os.pardir)

try:
	from Public_Tools.downloader import Downloader
	from Public_Tools.Crawler_Tools import normalize,same_domain,get_links
except ImportError:
	print 'import package error:[place:{code:12 or 13}]'

SLEEP_TIME = 3
def Threaded_Crawler(seed_url, link_regex=None, delay=5, max_depth=-1, max_urls=-1, headers=None, user_agent='wswp', proxy=None, num_retries=1, cache=None,max_threads=5):
    '''一般多线程爬虫，其中大部分与单线程连接爬虫一样，只是增加多线程控制'''
    crawl_queue = [seed_url]
    seen = {seed_url:0}
    num_urls = 0
    D = Downloader(delay=delay, user_agent=user_agent, proxies=proxy, num_retries=num_retries, cache=cache)

    def process_queue():
	    while True:
	        try:
	        	url = crawl_queue.pop()
	        except IndexError:
	        	break
	        else:
	        	html = D(url)
	        	links = []
	        	depth = seen[url]
	        	if depth != max_depth:
	        		if link_regex:
	        			links.extend(link for link in get_links(html) if re.match(link_regex, link))
	                for link in links:
	                    link = normalize(seed_url, link)
	                    if link not in seen:
	                        seen[link] = depth + 1
	                        if same_domain(seed_url, link):
	                        	crawl_queue.append(link)
    threads = []
    #当线程列表与link队列均为空时，退出多线程
    while threads or crawl_queue:
    	#从线程列表中将已经结束的线程清除掉
		for thread in threads:
			if not thread.is_alive():
				threads.remove(thread)
		#当线程数低于最大线程并且link队列里有值时进行循环
		while len(threads) < max_threads and crawl_queue:
			thread = threading.Thread(target=process_queue)
			thread.setDaemon(True)
			thread.start()
			threads.append(thread)
			
		time.sleep(SLEEP_TIME)