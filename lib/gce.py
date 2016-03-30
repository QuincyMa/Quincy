#!/usr/bin/env python
# -*- coding: UTF-8 -*-


#pip install --upgrade google-api-python-client
import os
import sys
import json
import time
import logger

from googleapiclient import discovery
from oauth2client.client import SignedJwtAssertionCredentials

class GceCompute(object):
    def __init__(self, service_account_email = None, gce_p12_file_path = None):
        if not service_account_email:
            service_account_email = os.getenv("service_account_email")
        if not gce_p12_file_path:
            gce_p12_file_path = os.getenv("gce_p12_file_path")    
        client_email = service_account_email
        key_path = os.path.expanduser(gce_p12_file_path)
        with open(key_path, 'r') as f:
            private_key = f.read()    
        credentials = SignedJwtAssertionCredentials(client_email, private_key,'https://www.googleapis.com/auth/compute')
        self.compute = discovery.build('compute', 'v1', credentials=credentials)
        self.zone = "us-central1-c"
        self.project = "openshift-gce-devel"
        self.network = "default"
        self.image = "libra-rhel7"
        self.machine_type = "n1-standard-1"


    def create_instance(self, gce_instance_name, gce_project=None,gce_zone=None, gce_network=None, gce_image=None, gce_machine_type=None):

        if not gce_project:
            gce_project = self.project

        if not gce_zone:
            gce_zone = self.zone
        resource_exist,resource_url = self.get_resource_url(gce_project,gce_zone,"zone")
        if resource_exist:
            zone_url = resource_url.replace('https://www.googleapis.com/compute/v1/', '')
            logger.info("zone: %s" %(zone_url)) 
        else:
            raise "Zone %s is not found in %s" %(gce_zone, gce_project)

        if not gce_network:
            gce_network = self.network
        resource_exist, resource_url = self.get_resource_url(gce_project,gce_network,"network")
        if resource_exist:
            network_url = resource_url.replace('https://www.googleapis.com/compute/v1/', '')
            logger.info("network: %s" %(network_url))
        else:
            raise "Network %s is not found in %s" %(gce_network, gce_project)

        if not gce_image:
            gce_image = self.image
        resource_exist, resource_url = self.get_resource_url(gce_project,gce_image,"image")
        if not resource_exist:
            from_image = False 
            resource_exist, resource_url = self.get_resource_url(gce_project,gce_image,"snapshot")
            if resource_exist:
                image_url = resource_url.replace('https://www.googleapis.com/compute/v1/', '')
                logger.info("snapshot: %s" %(image_url))
            else:
                raise "snapshot or image %s is not found in %s" %(gce_image,gce_project)
        else:
            image_url = resource_url.replace('https://www.googleapis.com/compute/v1/', '')
            from_image = True
            logger.info("image: %s" %(image_url))

                  
        if not gce_machine_type:
            gce_machine_type = self.machine_type
        resource_exist, resource_url = self.get_resource_url(gce_project,gce_machine_type,"machineType",gce_zone)
        if resource_exist:
            machine_type_url = resource_url.replace('https://www.googleapis.com/compute/v1/', '')
            logger.info("machineType: %s" %(machine_type_url))
        else:
            raise "machineType %s is not found in project %s zone %s" %(gce_machine_type,gce_project,gce_zone)


        self.delete_instance(gce_project,gce_zone,gce_instance_name)
        if from_image:
            params = {
                'name': gce_instance_name, 
                'sourceImage': image_url
            }
        else:
            params = {
                'name': gce_instance_name, 
                'sourceSnapshot': image_url
            }      
        res = self.compute.disks().insert(project=gce_project, zone=gce_zone,body=params).execute()
        self.wait_for_operation(gce_project,gce_zone,res['name'])
        for num in range(120):
            result = self.compute.disks().get(project=gce_project, zone=gce_zone,disk=gce_instance_name).execute()
            res = result
            if res['status'] == "READY":
                disk_url = res['selfLink']
                break
            if num == 199:
                raise "Fail to create disk from %s" %(gce_image)
            time.sleep(5)       
        params = {
            'name': gce_instance_name,
            'machineType': machine_type_url,
                'disks': [{
                'boot': True,
                'autoDelete': True,
                'source': disk_url
            }],
            'networkInterfaces': [{
                'network': network_url,
                'accessConfigs': [{'name': 'external'}]
            }]
        }
        res =  self.compute.instances().insert(project=gce_project, zone=gce_zone,body=params).execute()
        self.wait_for_operation(gce_project,gce_zone,res['name'])
        for num in range(120):
            result = self.compute.instances().get(project=gce_project, zone=gce_zone,instance=gce_instance_name).execute()
            res = result
            if res['status'] == "RUNNING":
                logger.debug("private IP:  %s, public IP: %s" %(res['networkInterfaces'][0]['networkIP'], res['networkInterfaces'][0]['accessConfigs'][0]['natIP']))
                return {
                    "private_ip": res['networkInterfaces'][0]['networkIP'],
                    "public_ip": res['networkInterfaces'][0]['accessConfigs'][0]['natIP'],
                    "hostname": gce_instance_name,
                    "public_hostname": gce_instance_name
                }
            if num == 199:
                raise "Fail to create instance: %s" %(gce_instance_name)
            time.sleep(5)



    def wait_for_operation(self, project, zone, operation):
        for num in range(120):
            res = self.compute.zoneOperations().get(project=project,zone=zone,operation=operation).execute()
            if res['status'] == "DONE":
                break
            time.sleep(5)

    def get_resource_url(self, project, resource_name, resource_type, zone=None):
        filter_str = "name eq %s" %(resource_name)
        if resource_type == "snapshot":
            result = self.compute.snapshots().list(project=project,filter=filter_str).execute()
        elif resource_type == "network":
            result = self.compute.networks().list(project=project,filter=filter_str).execute()
        elif resource_type == "image":
            result = self.compute.images().list(project=project,filter=filter_str).execute()
        elif resource_type == "zone":
            result = self.compute.zones().list(project=project,filter=filter_str).execute()
        elif resource_type == "machineType":
            result = self.compute.machineTypes().list(project=project,zone=zone,filter=filter_str).execute()
        elif resource_type == "instance":
            result = self.compute.instances().list(project=project, zone=zone,filter=filter_str).execute()
        else:
            pass
        
        if "items" in result:
            return True, result['items'][0]['selfLink']
        return False,None

    def delete_instance(self, project, zone, instance):
        resource_exist, instance_url = self.get_resource_url(project,instance,"instance",zone)
        if resource_exist:
            result = self.compute.instances().delete(project=project, zone=zone,instance=instance).execute()
            self.wait_for_operation(project,zone,result['name'])



if __name__ == "__main__":
    test = GceCompute("1043659492591-r0tpbf8q4fbb9dakhjfhj89e4m1ld83t@developer.gserviceaccount.com", "/root/.gce/openshift-gce-devel-f4fa17c08d7f.p12")
    test.create_instance("xiama-test-n2")