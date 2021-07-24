#!/bin/usr env python
# -.- coding: utf-8 -.-
import utils

if utils.is_py2:
    import urllib2
    from urllib import quote, urlencode
elif utils.is_py3:
    from urllib import request as urllib2
    from urllib.parse import quote, urlencode


def stop(port):
    req = urllib2.Request('http://127.0.0.1:' + port + '/stop')
    urllib2.urlopen(req)


def sync(content, port):
    utils.log(content)
    req = urllib2.Request('http://127.0.0.1:' + port + '/sync', data=content)
    urllib2.urlopen(req)
