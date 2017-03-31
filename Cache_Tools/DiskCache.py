#!/user/bin/env python
#-*- coding:utf-8 -*-
import urlparse
import os
import re

try:
    import cPickle as pickle
except:
    import pickle

from datetime import datetime, timedelta

class DiskCache(object):
    '''利用硬盘进行网页信息的缓存'''
    def __init__(self, cache_dir='cache', expires = timedelta(days=7)):
        self.cache_dir = cache_dir #缓存的路径以及文件名
        self.max_length = 200      #最大长度
        self.expires = expires     #保存期限

    def url_to_path(self, url):
        '''将url转换为文件路径'''
        components = urlparse.urlsplit(url)
        path = components.path

        #当路径以"/"结尾时，给路径添加index.html
        if not path:
            path = '/index.html'
        elif path.endswith('/'):
            path += 'index.html'

        #将地址 路径 参数 组合在一起
        filename = components.netloc + path +components.query
        #利用正则表达式，将以'/'开头的字符串匹配
        filename = re.sub('[^/0-9a-zA-Z\-.,;_]', '_', filename)
        #以"/"分割字符串，从而建立文件路径
        filename = '/'.join(segment[:255] for segment in filename.split('/'))

        return os.path.join(self.cache_dir, filename)

    def __getitem__(self, url):
        #获取url对应的缓存结果
        path = self.url_to_path(url)
        if os.path.exists(path):
            with open(path, 'rb') as fp:
                result, timestamp = pickle.loads(fp.read())
                if self.has_expired(timestamp):
                    raise KeyError(url + ' has expired')
                else:
                    return result
        else:
            raise KeyError(url+'does not exist')

    def __setitem__(self, url, result):
        #设置url对应的缓存结果
        path = self.url_to_path(url)
        folder = os.path.dirname(path)

        if not os.path.exists(folder):
            os.makedirs(folder)
        timestamp = datetime.utcnow()
        data = pickle.dumps((result,timestamp))

        with open(path, 'wb') as fp:
            fp.write(data)

    def has_expired(self, timestamp):
        #判断缓存文件是否过期
        return datetime.utcnow() > timestamp + self.expires