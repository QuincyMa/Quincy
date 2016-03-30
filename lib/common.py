#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import httplib
import json
import socket
import time
import datetime
from urlparse import urlparse
#import urllib
import base64

def run_request(url, method, params={}, options={}):
    urls = urlparse(url)
    host = urls.netloc
    path = urls.path

    header = {}
    if options == {}:
        header = {'Accept':'application/json', 'Content-Type':'application/json'}
    else:
        if not options.has_key("accept"):
            header['Accept'] = 'application/json'
        else:
            header['Accept'] = options['Accept']

        if not options.has_key('Content-Type'):
            header['Content-Type'] = 'application/json'
        else:
            header['Content-Type'] = options['Content-Type']

        if options.has_key('Authorization'):
            header['Authorization'] = options['Authorization']
        elif options.has_key('token'):
            header['Authorization'] = 'Bearer ' + options['token']
        elif options.has_key('user'):
            base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
            authheader =  "Basic %s" % base64string
            header["Authorization"] = authheader
        elif options.has_key('x-token'):
            header['X-Auth-Token'] = options['x-token']

    if urls.scheme == "http":
        conn = httplib.HTTPConnection(host)
    else:
        conn = httplib.HTTPSConnection(host)

    params = json.dumps(params)
    conn.request(method, path, params, header)
    res = conn.getresponse()
    respone = res.read()
    conn.close()
    return res.status, respone


def wait_for_host(host, port=22, delay=5, timeout=600):
    connected = False
    end = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    while datetime.datetime.now() < end:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect( (host, port) )
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            connected = True
            break
        except:
            time.sleep(1)
            pass
        time.sleep(delay)
    return connected



if __name__ == "__main__":
    print wait_for_host("openshift-150.lab.sjc.redhat.com",timeout=20)
