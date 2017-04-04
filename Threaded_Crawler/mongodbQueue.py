#!user/bin/env python
#-*- coding:utf-8 -*-
from datetime import datetime,timedelta
from pymongo import MongoClient,errors

class MongoQueue(object):
	'''MongoDB数据库作为link缓存替代原有列表方法列表'''
	#三种存储状态 0:新加入 1:正在请求 2:请求完成
	OUTSTANDING,PROCESSING,COMPLETE = range(3)

	def __init__(self, client=None, self_db=None, timeout=1200):
		self.client = MongoClient() if client is None else client
		self.db = self.client.cache if self_db is None else self_db
		self.timeout = timeout
		self.repair()
	#此内置函数表示当对象当作判断条件时，会执行这个函数
	def __nonzero__(self):
		record = self.db.crawl_queue.find_one({'status':{'$ne':self.COMPLETE}})
		return True if record else False

	#将url插入到队列中
	def push(self, url):
		try:
			self.db.crawl_queue.insert({'_id':url,'status':self.OUTSTANDING})
		except errors.DuplicateKeyError as e:
			#当发生此类异常时，说明已经插入相同的url作为"_id",不能有相同的id,不用做处理
			pass
	#将队列中的url返回
	def pop(self):
		record = self.db.crawl_queue.find_and_modify(query={'status':self.OUTSTANDING},update={'$set':{'status':self.PROCESSING,'timeout':datetime.now()}})
		if record:
			return record['_id']
		else:
			#当出现队列中url均为已请求状态时，抛出异常
			self.repair()
			raise KeyError()
	#将url标记为已请求完成
	def complete(self, url):
		self.db.crawl_queue.update({'_id':url},{'$set':{'status':self.COMPLETE}})
	#将队列中的数据进行更新，查看已经超时的数据，并更新
	def repair(self):
		record = self.db.crawl_queue.find_and_modify(query={'timeout':{'$lt':datetime.now() - timedelta(seconds=self.timeout)},'status':self.COMPLETE},update={'$set':{'status':self.OUTSTANDING}})
		if record:
			print 'Released:',record['_id']

	def rollback(self, url):
		record = self.db.crawl_queue.find_and_modify(query={'_id':url}, update={'$set':{'status':self.OUTSTANDING}})
		if record:
			print 'rollback success:{}'.format(url)
		else:
			print 'rollback error: Check that database'
	#清除mongodb缓存队列数据库
	def clear(self):
		self.db.crawl_queue.drop()