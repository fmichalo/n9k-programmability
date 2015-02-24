#!/usr/bin/env python
#
# Copyright (C) 2014 Cisco Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This script loops through every Ethernet interface on the switch and prints 
# either the runts, collisions, or crc errors for every interface in fuction of
# the first argument (crc, runts or coll).  The second argument is an optional 
# integer and if is sent, only the interfaces will more than N [ runts, 
# collisions, or crc errors ] will be displayed.  To use :
#
# 1. Chage arguemnts value of connexion (ip, and credentials)
# 2. Execute using:
# python interface_stats.py {runts | crc | coll} [int]
# 
#

import sys
sys.path.append("./cisco")
sys.path.append("./utils")
import xmltodict
import json
from device import Device


if __name__ == "__main__":
    switch = Device(username='admin', password='cisco', ip='172.17.253.86')
    switch.open()
    length = len(sys.argv)

    if  length == 1:
        print '\n Input Requires an option. \n\n Available Options: '
        print ' - crc\n - runts\n - coll\n'
    else:
        args = sys.argv
        getdata = switch.show('show interface')
        show_int_dict = xmltodict.parse(getdata[1])
        stats = show_int_dict['ins_api']['outputs']['output']['body']

        #stats = json.loads(clid('show interface'))

        if args[1] == 'help':
            print '\n Available Options: ' + '\n - crc ' + '\n - runts\n - coll\n'
        else:
        	if not (args[1] == 'crc' or args[1] == 'runts' or args[1] == 'coll'):
  	            print '\nInvalid Option'
  	            print 'Input Requres a Valid Option'
  	            print '\n Available Options: ' + '\n - crc ' + '\n - runts\n - coll\n'
  	        else:
  	            for each in stats['TABLE_interface']['ROW_interface']:
  	                if each['interface'].startswith('Eth'):
  	                	delta = 15 - len(each['interface'])
      	    			spaces = delta * ' '
      	    			if length == 2:
      	    				occurences = 0
      	    			elif length == 3:
      	    			    occurences = args[2]
      	    			if args[1] == 'crc' and each['eth_crc'] >= occurences:
      	    				print each['interface'] + ': ' + spaces + 'CRC errors: ' + each['eth_crc']
      	    			elif args[1] == 'runts' and each['eth_runts'] >= occurences:
      	    				print each['interface'] + ': ' + spaces + 'runts: ' + each['eth_runts']	 
      	    			elif args[1] == 'coll' and each['eth_coll'] >= occurences:
      	    				print each['interface'] + ': ' + spaces + 'collisions: ' + each['eth_coll']

