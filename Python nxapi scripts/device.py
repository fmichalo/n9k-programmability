#!/usr/bin/env python
#
# Copyright (C) 2013 Cisco Systems Inc.
# All rights reserved
#
#
# Scripts for simplified connection to the switch 
# This use the new and better version of the NXAPI Utils 
# Look at utils/nxapi_utils for see the new and old version of the tool. 
# NXAPITransport is depreciated and now NXAPI should be used
# 


import xmltodict
import json
#import yaml
import sys

sys.path.append("./cisco")
sys.path.append("./utils")

from nxapi_utils import NXAPI

class Device():
  
  def __init__(self,username='cisco',password='!cisco123!',ip='192.168.200.50'):
    
    self.username = username
    self.password = password
    self.ip = ip
    
  def open(self):

    self.sw1 = NXAPI()
    self.sw1.set_target_url('http://'+self.ip+'/ins')
    self.sw1.set_username(self.username)
    self.sw1.set_password(self.password)

  def show(self,command,fmat='xml'):

    self.sw1.set_msg_type('cli_show')
    self.sw1.set_out_format(fmat)
    self.sw1.set_cmd(command)

    return self.sw1.send_req()

  def conf(self,command,fmat='xml'):

    self.sw1.set_msg_type('cli_conf')
    self.sw1.set_out_format(fmat)
    self.sw1.set_cmd(command)

    return self.sw1.send_req()