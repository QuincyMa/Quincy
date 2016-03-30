#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import common
from urlparse import urlparse
import time
import re


class OpenStack(object):
    def __init__(self, url, user, password, tenant_id):
        self.url = url
        self.user = user
        self.passwd = password
        self.tenant_id = tenant_id
        self.token, self.apiurl = self.__get_token__();

    def __get_token__(self):
        params = {"auth": {"tenantId":self.tenant_id, "passwordCredentials":{"username":self.user, "password":self.passwd }}}
        status, res = common.run_request(self.url, 'POST', params = params)
        try:
            result = json.loads(res)
            token = result['access']['token']['id']
            for server in result['access']['serviceCatalog']:
                if server['name'] == "nova" and server['type'] == "compute":
                    apiurl = server['endpoints'][0]['publicURL']
        except:
            raise

        return token, apiurl

    def get_obj_ref(self, objectname, objtype):
        url = self.apiurl + "/" + objtype
        status, res = common.run_request(url,'GET', options ={'x-token': self.token})
        try:
            result = json.loads(res)
            for obj in result[objtype]:
                if obj['name'] == objectname:
                    return obj["links"][0]["href"]
            return None
        except:
            raise

    def get_instance_ref(self, image_name):
        return self.get_obj_ref(image_name, 'servers')

    def get_flavor_ref(self, flavor_name):
        return self.get_obj_ref(flavor_name, 'flavors')

    def get_image_ref(self, imageName):
        return self.get_obj_ref(imageName, 'images')

    def delete_instance(self, instance_name):
        params = {}
        url = self.get_obj_ref(instance_name,"servers")
        if url == None:
            return True
        common.run_request(url, "DELETE", options ={'x-token': self.token})
        for i in range(30):
            time.sleep(20)
            if self.get_obj_ref(instance_name,"servers"):
                pass
            else:
                return True
            self.delete_instance(instance_name)
        return False

    def create_instance(self,instanceName, imageName, falvorName, keyName):
        self.delete_instance(instanceName)
        image_href = self.get_image_ref(imageName)
        falvor_href = self.get_flavor_ref(falvorName)
        params = {'server': {'name': instanceName,'key_name':keyName ,'imageRef':image_href, 'flavorRef':falvor_href}}
        url = self.apiurl + '/' + 'servers'
        code, res = common.run_request(url, "POST", params, options ={'x-token': self.token})
        result = json.loads(res)
        server_id = result["server"]["id"]
        params = {}
        url = self.apiurl + '/' + 'servers/' + server_id
        for num in range(120):
            status, res = common.run_request(url, "GET", params, options ={'x-token': self.token})
            result = json.loads(res)
            if result["server"]["status"] == "ERROR":
                self.create_instance(instance_name, image_name, flavor_name, key)
            elif result["server"]["status"] == "ACTIVE":
                private_ip, public_ip = self.get_instance_ip(result['server']['links'][0]['href'], True, True)
                return {
                    "private_ip": private_ip,
                    "public_ip": public_ip,
                    "hostname": "",
                    "public_hostname": ""
                }
            time.sleep(5)

    def assign_ip(self,instance_name, ref = False):
        assigning_ip = None
        url = self.apiurl + '/os-floating-ips'
        code, res = common.run_request(url, "GET", options ={'x-token': self.token})
        result = json.loads(res)
        for ip in result['floating_ips']:
            if ip['instance_id'] == None:
                assigning_ip = ip['ip']
                break
        params = { "addFloatingIp": {"address": assigning_ip }}
        if not ref:
            instance_href = self.get_obj_ref(instance_name, 'servers') + "/action"
        else:
            instance_href = instance_name + "/action"
        common.run_request(instance_href, "POST",params, options ={'x-token': self.token})

    def get_instance_ip(self, instance_name,ref = False, assignip = False):
        if not ref:
            instance_href = self.get_instance_ref(instance_name)
        else:
            instance_href = instance_name
        status, res = common.run_request(instance_href, "GET", options ={'x-token': self.token})
        result = json.loads(res)
        for key in  result['server']['addresses'].keys():
            if re.match(r"([0-9]{1,3}\.){3,}[0-9]" ,result['server']['addresses'][key][0]['addr']):
                if len(result['server']['addresses'][key]) == 2:
                    return result['server']['addresses'][key][0]['addr'],result['server']['addresses'][key][1]['addr']
                else:
                    if assignip:
                        self.assign_ip(result['server']['links'][0]['href'], True)
                        return self.get_instance_ip(result['server']['links'][0]['href'],True)
                    else:
                        return result['server']['addresses'][key][0]['addr'],None


if __name__ == "__main__":
    test = OpenStack('http://0.3.0.3:5000/v2.0/tokens', 'jiaiu','test', '68408e6815dd4078b911d8ba4228766f')
    #test.create_instance("ose-xiama-test","RHEL-6.5-20140729" , 'm1.medium','libra')
    print test.get_instance_ip("ose-xia-test")
