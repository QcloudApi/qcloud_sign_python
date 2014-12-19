#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#
#     FileName: QcloudSign.py
#         Desc: 腾讯云 api 联调工具
#
#       Author: gavinyao
#        Email: gavinyao@tencent.com
#
#      Created: 2014-08-19 15:40:02
#      Version: 0.0.1
#      History:
#               0.0.1 | gavinyao | 2014-08-19 15:40:02 | initialization
#
#=============================================================================*/
'''
import urllib
import urllib2
import httplib
import binascii
import hashlib
import hmac
import time
import random
import sys
import json

##
# @brief 拼出签名字符串原文
# @author gavinyao@tencent.com
# @date 2014-08-20 12:25:14
#
# @param requestMethod
# @param requestHost
# @param requestPath
# @param params
#
# @return
def makePlainText(requestMethod, requestHost, requestPath, params):
    str_params = "&".join(k + "=" + str(params[k]) for k in sorted(params.keys()))

    source = '%s%s%s?%s' % (
            requestMethod.upper(),
            requestHost,
            requestPath,
            str_params
            )
    return source

##
# @brief 签名
# @author gavinyao@tencent.com
# @date 2014-08-20 12:24:53
#
# @param requestMethod 请求方法 POST/GET
# @param requestHost 请求主机
# @param requestPath 请求路径
# @param params 请求参数
# @param secretKey
#
# @return
def sign(requestMethod, requestHost, requestPath, params, secretKey):
    source = makePlainText(requestMethod, requestHost, requestPath, params)
    hashed = hmac.new(secretKey, source, hashlib.sha1)
    return binascii.b2a_base64(hashed.digest())[:-1]


def main():
    # secretId 和 secretKey
    secretId = 'YOUR_SECRET_ID'
    secretKey = 'YOUR_SECRET_KEY'

    requestMethod = 'POST'
    requestHost = 'cvm.api.qcloud.com'
    requestPath = '/v2/index.php'

    # 请求参数
    params = {
            'SecretId': secretId,
            'Timestamp': int(time.time()),
            'Nonce': random.randint(1, sys.maxint),
            'Region': 'gz',
            'Action': 'DescribeInstances'
            }


    plainText = makePlainText(requestMethod, requestHost, requestPath, params)
    signText = sign(requestMethod, requestHost, requestPath, params, secretKey)
    print "原文:%s" % plainText
    print "签名:%s" % signText

    params['Signature'] = signText

    headers = {"Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"}

    # 发送请求
    httpsConn = None
    try:
        httpsConn = httplib.HTTPSConnection(host = requestHost, port = 443)
        if requestMethod == "GET":
            params['Signature'] = urllib.quote(signText)

            str_params = "&".join(k + "=" + str(params[k]) for k in sorted(params.keys()))
            url =  'https://%s%s?%s' % (requestHost, requestPath, str_params)
            httpsConn.request("GET", url)
        elif requestMethod == "POST":
            params = urllib.urlencode(params)
            httpsConn.request("POST", requestPath, params, headers)

        response = httpsConn.getresponse()
        data = response.read()
        # print data
        jsonRet = json.loads(data)
        print json.dumps(jsonRet, indent = 4, ensure_ascii=False)

    except Exception, e:
        print e
    finally:
        if httpsConn:
            httpsConn.close()

if __name__ == '__main__':
    main()

