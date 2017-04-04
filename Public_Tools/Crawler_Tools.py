#!/user/bin/env python
#-*- coding:utf-8 -*-
import urlparse
import robotparser
import re
def get_robot(url):
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp

def normalize(seed_url, link):
    link, frag = urlparse.urldefrag(link) # remove hash to avoid duplicates
    return urlparse.urljoin(seed_url, link)

def same_domain(url1, url2):
    return urlparse.urlparse(url1).netloc == urlparse.urlparse(url2).netloc

def get_links(html):
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)

    return webpage_regex.findall(html)