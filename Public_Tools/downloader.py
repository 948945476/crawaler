#!/user/bin/env python
#-*- coding:utf-8 -*-
import urlparse
import urllib2
import random
import time
import socket

from datetime import datetime

DEFAULT_AGENT = 'wswp'  #代理
DEFAULT_DELAY = 5       #延迟时间
DEFAULT_RETRIES = 2     #重复次数
DEFAULT_TIMEOUT = 20    #等待时间
class Downloader(object):
    '''下载类，提供网页下载功能'''
    def __init__(self, delay=DEFAULT_DELAY, user_agent=DEFAULT_AGENT, proxies=None, num_retries=DEFAULT_RETRIES, timeout=DEFAULT_TIMEOUT, opener=None, cache=None):
        socket.setdefaulttimeout(timeout) #设置socket等待时间
        self.throttle = Throttle(delay)   #设置两次请求之间的等待时间并甄别bad_url
        self.user_agent = user_agent      #设置用户代理
        self.proxies = proxies            #设置代理字典
        self.num_retries = num_retries    #设置重复次数
        self.opener = opener
        self.cache = cache
    #将类以函数形式运行
    def __call__(self, url):
        result = None
        if self.cache:
            #当有缓存机制时尝试从缓存中取出url对应的网页缓存，没有则会引发KeyError异常
            try:
                result = self.cache[url]
            except KeyError:
                pass
            else:
                if (self.num_retries > 0 and 500 <= result['code'] < 600) or result['code'] == None:
                    #如果重复请求次数有效，请求码为服务器问题
                    result = None
        if not result:
            #当结果为空时，需要进行下载
            self.throttle.wait(url)
            proxy = random.choice(self.proxies) if self.proxies else None
            headers = {'User-agent': self.user_agent}
            result = self.download(url, headers, proxy=proxy, num_retries=self.num_retries)
            if self.cache:
                #当有缓存机制时，将结果存入缓存中
                self.cache[url] = result
        return result['html']


    def download(self, url, headers, proxy, num_retries, data=None):
        '''下载函数，提供url返回结果，返回结果不一定为正确结果'''
        print 'Downloading:', url
        request = urllib2.Request(url, data, headers or {})
        opener = self.opener or urllib2.build_opener()
        if proxy:
            proxy_params = {urlparse.urlparse(url).scheme: proxy}
            opener.add_handler(urllib2.ProxyHandler(proxy_params))
        try:
            response = opener.open(request)
            html = response.read()
            code = response.code
        except urllib2.HTTPError,e:
            #当出现HTTP请求错误时暂时没有很好的鉴别方式，待完善
            html = ''
            code = None
            print 'Download error[HTTP]:', str(e)
            print 'not make the Page！'
        except urllib2.URLError, e:
            #当出现URL错误时，甄别是否为超时请求
            print 'Download error[URL:%s]:%s'%(url,str(e))
            code = None
            html = ''
            if hasattr(e, 'reason'):
                if str(e.reason) == 'timed out':
                    code = 504
                if num_retries > 0 and 500 <= code < 600:
                    self.throttle.wait(url)
                    return self.download(url, headers, proxy, num_retries-1, data)
            else:
                code = None
        return {'html': html, 'code': code}


class Throttle:
    '''在两次相同请求之中，进行适当“休息”'''
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}
        
    def wait(self, url):
        domain = urlparse.urlsplit(url).netloc
        last_accessed = self.domains.get(domain)
        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()