#!/usr/bin/env
# -*- coding: UTF-8 -*-

import jenkins
import os


"""
operate jenkins via python-jenkins packages

password can be PASSWD or token of user
Pls refer to http://python-jenkins.readthedocs.org/en/latest/
pip install python-jenkins
"""

server = jenkins.Jenkins('https://openshift-qe-jenkins.rhev-ci-vms.eng.rdu2.redhat.com', username='xiama', password='894bc1b312e95eeed7907250dc52cfb9')
params =  {
  "ENV_INFO": "all:10.66.79.149,node1:10.66.79.138,node2:10.66.79.155",
  "INSTALL_COMPONENT": "all",
  "BUILD_VER": "2015-04-02.1",
  "DOMAIN_NAME": "ose22-auto.com.cn",
  "OSE_VERSION": "2.2",
  "LOCAL_FLAG": True,
  "CONF_NOTIFY": "false",
  "Trigger_Smoke": "true",
  "Trigger_Testing_Flag": "yes"
}
print server.build_job("OSE_SetupTestEnv", parameters = params)
