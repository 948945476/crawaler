#!/user/bin/env python
#-*- coding:utf-8 -*-
import time
from datetime import datetime

#添加三种爬虫
from Link_Crawler.Links_Crawler import link_crawler
from Threaded_Crawler.Threade_MongoDB_Crawler import Threaded_Crawler as TDBC
from Threaded_Crawler.Threaded_Crawler import Threaded_Crawler as TC
#添加两类缓存
from Cache_Tools.DiskCache import DiskCache
from Cache_Tools.MongoDBCache import MongoCache

def main(i, max_threads_num):
	#爬虫的开始时间
	start = time.clock()
	#提示多线程爬虫线程数(单线程即使输出也无效)
	print 'make %d threads'%(max_threads_num)
	
	#操作符判断选定所执行的爬虫
	if i==0:
		link_crawler('http://example.webscraping.com/', '/(index|view)', cache=DiskCache())
	elif i==1:
		link_crawler('http://example.webscraping.com/', '/(index|view)', cache=MongoCache())
	elif i==2:
		TC('http://example.webscraping.com/', '/(index|view)', cache=DiskCache(), max_threads=max_threads_num)
	elif i==3:
		TDBC('http://example.webscraping.com/', '/(index|view)', cache=MongoCache(), max_threads=max_threads_num)
	else:
		print 'Command is null'
	
	#爬虫结束时间
	end = time.clock()
	print 'run_time: %f s'%(end - start)

if __name__ == '__main__':
	now = datetime.now()
	otherStyleTime = now.strftime("%Y-%m-%d %H:%M:%S")
	print '--now_time:',otherStyleTime
	print '----------------------------------------------------------------------------------'
	print '|-----------------------------------Command List---------------------------------|'
	print '|-  0 : Ordinary link crawler, using hard disk to do the cache ------------------|'
	print '|-  1 : Ordinary link crawler, using MongoCache database to do the cache --------|'
	print '|-  2 : Multi-threaded link crawler, using hard disk to do the cache ------------|'
	print '|-  3 : Multi-threaded link crawler, using MongoCache database to do the cache --|'
	print '|--------------------------------------------------------------------------------|'
	print '--------------------!Worring:0 and 1 max_threads_num is null----------------------'
	print '--Let\'s start the crawler!'
	i = input('--please input Command:')
	tn = 1
	tn = input('--please input max_threads_num:')
	main(int(i), int(tn))