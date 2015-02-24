# Copyright (C) 2013 Cisco Systems Inc.
# All rights reserved
# Usage of NXAPITransport is depreciated, now use NXAPI (show interface_stats.py and nxapi_facts.py for examples)
import sys

sys.path.append("./cisco")
sys.path.append("./utils")

############## DEPRECIATED ################
from nxapi_utils import NXAPITransport 
##########################################


from cisco.interface import Interface

################### 
# NXAPI init block
###################
target_url = "http://172.17.253.86/ins"
username = "admin"
password = "cisco"
NXAPITransport.init(target_url=target_url, username=username, password=password)
###################
################### 
# cli/clip/clid are changed a bit, but largely the same
###################
print NXAPITransport.cli("show version")

print NXAPITransport.clip("show interface brief")

#NXAPITransport.clic("conf t ;interface eth4/1 ;no shut")

print NXAPITransport.clid("show version")
################### 
# Below is exactly the same as the usage on the switch. Do whatever you
# are already doing on the switch right now!
###################
print Interface.interfaces()

i = Interface("Ethernet1/96")

print i.show(key="eth_mtu")

i.set_description(d="Port serveur")



