#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import boto3

class AwsEc2(object):
    def __init__(self):
        self.ec2 = boto3.resource("ec2")
        self.image_id = "ami-01743f64"
        self.instance_type = "m3.medium"
        self.subnet_id = "subnet-cf57c596"
        self.security_groups = ["default"]
        self.key_name = "libra"

    def create_instance(self, instance_name, image_id=None, instance_type=None, subnet_id=None, security_groups=None, key_name=None):
        self.delete_instance(instance_name)
        if not image_id:
            image_id = self.image_id
        if not instance_type:
            instance_type = self.instance_type
        if not subnet_id:
            subnet_id = self.subnet_id
        vpc_id = self.ec2.Subnet(subnet_id).vpc_id

        if not security_groups:
            security_groups = self.security_groups
        filters = [
            {'Name': 'vpc-id', 'Values': [vpc_id] },
            {'Name': 'group-name', 'Values': security_groups }
        ]
        security_groups_ids = []
        security_groups = self.ec2.security_groups.filter(Filters=filters)
        for group in security_groups:
            security_groups_ids.append(group.id)
        if not security_groups_ids:
            raise "Can not found  security_groups in specified Subnet"

        if not key_name:
            key_name = self.key_name

        instance = self.ec2.create_instances(ImageId=image_id,
            MinCount=1,
            MaxCount=1,
            KeyName=key_name,
            SecurityGroupIds=security_groups_ids,
            InstanceType=instance_type,
            SubnetId=subnet_id)
        instance[0].wait_until_running()
        instance[0].create_tags(Tags=[{'Key': 'Name', 'Value':instance_name}])

        return {
            'private_ip': instance[0].private_ip_address,
            'public_ip': instance[0].public_ip_address,
            'hostname': instance[0].private_dns_name,
            'public_hostname':instance[0].public_dns_name
        }

    def delete_instance(self, instance_name):
        filters = [
            {'Name': 'instance-state-name', 'Values': ['running']},
            {'Name': 'tag-key', 'Values': ['Name']},
            {'Name': 'tag-value', 'Values': ['instance_name']}
        ]
        instances = self.ec2.instances.filter(Filters=filters)
        for instance in instances:
            instance.stop()
            instance.wait_until_stopped()


if __name__ == "__main__":
    test = AwsEc2()
    print test.create_instance("xiama-test-master")
