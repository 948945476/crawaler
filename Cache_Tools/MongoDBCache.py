#!/user/bin/env python
#-*- coding:utf-8 -*-
import os
import re
import time
import pymongo

from bson.binary import Binary
from datetime import datetime, timedelta
from pymongo import MongoClient

class MongoCache(object):
	"""利用MongoDB数据库进行缓存"""
	def __init__(self, client=None, expires=timedelta(days = 2)):
		self.client = MongoClient('localhost',27017) if client is None else client
		self.db = self.client.cache
		#建立以时间戳为标准的索引，从而可以实现过期自动清理
		self.db.webpage.create_index([('timestamp',pymongo.ASCENDING)],expireAfterSeconds=expires.total_seconds())

	def __getitem__(self,url):
		record = self.db.webpage.find_one({'_id':url})
		if record:
			return record['result']
		else:
			raise KeyError(url+' does not exist')

	def __setitem__(self, url, result):
		record = {'result':result,'timestamp':datetime.now()}
		self.db.webpage.update({'_id':url}, {'$set':record}, upsert=True)