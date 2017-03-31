#!/user/bin/env python
#-*- coding:utf-8 -*-
import urlparse
import robotparser
import re
def get_robot(url):
	'''获取网站的robot.txt并确定其可用性(此功能不是必须的)'''
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp

def normalize(seed_url, link):
	'''将连接与基url组合'''
    link, frag = urlparse.urldefrag(link) # remove hash to avoid duplicates
    return urlparse.urljoin(seed_url, link)

def same_domain(url1, url2):
	'''比较两个url的基地址是否相同'''
    return urlparse.urlparse(url1).netloc == urlparse.urlparse(url2).netloc

def get_links(html):
	'''使用正则表达式,去匹配页面中的连接'''
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)

    return webpage_regex.findall(html)