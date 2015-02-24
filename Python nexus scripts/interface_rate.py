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
# This script prints interface throughput/packet rate statistics in an
# easy to read list format on NX-OS platforms. Without argument all interfaces 
# will be shown and with an interface nam as argument, only these interface will be 
# printed.
# To use:
#
# 		1. Copy script to NX-OS switch bootflash:scripts
# 		2. Execute using:
# python bootflash:scripts/interface_rate.py [interfaceName]
#

from __future__ import division
try:
    from cli import cli
except ImportError:
    from cisco import cli
import sys
import xml.etree.cElementTree as ET

if len(sys.argv) > 1 and sys.argv[1]== 'help':
    print '\n------------------------------- HELP --------------------------------'
    print 'Without argument, all interfaces will be displayed'
    print 'Argument is optional and must be an interface name (like Ethernet1/1)'
    print '---------------------------------------------------------------------'
else:
    # Handle cli() type inconsistencies
    def make_cli_wrapper(f):
        if type(f("show clock")) is tuple:
            def cli_wrapper(*args, **kwargs):
                return f(*args, **kwargs)[1]
            return cli_wrapper
        return f

    cli = make_cli_wrapper(cli)

    # Get interface information in XML format
    print
    print 'Collecting and processing interface statistics ...'
    print
    sys.stdout.flush()
    raw = cli('show interface | xml | exclude "]]>]]>"')

    # Load and parse XML
    tree = ET.ElementTree(ET.fromstring(raw))
    data = tree.getroot()
    
    # Find and display interface rate information
    if_manager = '{http://www.cisco.com/nxos:1.0:if_manager}'
    table = "{0:16}{1:9}{2:9}{3:9}{4:9}{5:9}{6:9}{7:9}"
    result = False
    print '---------------------------------------------------------------------------'
    print table.format("Port", "Intvl", "Rx Mbps", "Rx %", "Rx pps", "Tx Mbps", "Tx %", "Tx pps")
    print '---------------------------------------------------------------------------'
    for i in data.iter(if_manager + 'ROW_interface'):
        try:
            if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == i.find(if_manager + 'interface').text): 
                interface = i.find(if_manager + 'interface').text
                bw = int(i.find(if_manager + 'eth_bw').text)
                rx_intvl = i.find(if_manager + 'eth_load_interval1_rx').text
                rx_bps = int(i.find(if_manager + 'eth_inrate1_bits').text)
                rx_mbps = round((rx_bps / 1000000), 10)
                rx_pcnt = round((rx_bps / 1000) * 100 / bw, 10)
                rx_pps = i.find(if_manager + 'eth_inrate1_pkts').text
                tx_intvl = i.find(if_manager + 'eth_load_interval1_tx').text
                tx_bps = int(i.find(if_manager + 'eth_outrate1_bits').text)
                tx_mbps = round((tx_bps / 1000000), 10)
                tx_pcnt = round((tx_bps / 1000) * 100 / bw, 10)
                tx_pps = i.find(if_manager + 'eth_outrate1_pkts').text
                print table.format(interface, rx_intvl + '/' + tx_intvl, str(rx_mbps), str(rx_pcnt) + '%', rx_pps, str(tx_mbps), str(tx_pcnt) + '%', tx_pps)
                sys.stdout.flush()
                result = True
        except AttributeError:
            pass
    if result == False: 
        print '\nERROR:NO INTERFACE WITH THIS NAME.'
