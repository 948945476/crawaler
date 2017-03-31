#!/user/bin/env python
#-*- coding:utf-8 -*-
import re
import os
import sys

sys.path.append(os.pardir)
try:
    from Public_Tools.downloader import Downloader
    from Public_Tools.Crawler_Tools import *
except ImportError:
    print 'import package error:[place:{code:9 or 10}]'

def link_crawler(seed_url, link_regex=None, delay=5, max_depth=-1, max_urls=-1, headers=None, user_agent='wswp', proxy=None, num_retries=1, cache=None):
    '''以连接进行爬取的普通单线程爬虫'''
    crawl_queue = [seed_url]
    seen = {seed_url:0}
    num_urls = 0
    #查看网站的robot.txt 不是所有网站都适用
    rp = get_robot(seed_url)
    #建立 Downloader 类的一个对象
    D = Downloader(delay=delay, user_agent=user_agent, proxies=proxy, num_retries=num_retries, cache=cache)
    
    while crawl_queue:
        url = crawl_queue.pop()
        #如果网站拥有 robot.txt 并且代理符合网站规范则能够进行之后的操作，不是必须的
        if rp.can_fetch(user_agent, url):
            html = D(url)
            links = []

            depth = seen[url]
            #爬取最大深度判断，当前url是否已经到达规定的最大深度
            if depth != max_depth:
                if link_regex:
                    #根据正则表达式判断连接参数与实际参数是否匹配
                    links.extend(link for link in get_links(html) if re.match(link_regex, link))
                for link in links:
                    link = normalize(seed_url, link)
                    if link not in seen:
                        seen[link] = depth + 1
                        # check link is within same domain
                        if same_domain(seed_url, link):
                            # success! add this new link to queue
                            crawl_queue.append(link)

            #当下载连接数达到最大时退出下载
            num_urls += 1
            if num_urls == max_urls:
                break
        else:
            print 'Blocked by robots.txt:', url