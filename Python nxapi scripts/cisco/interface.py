# Copyright (C) 2013 Cisco Systems Inc.
# All rights reserved
import re,datetime
import nxos_utils
from .nxcli import *

def get_valid_port(port):
    ''' Validate and return correct port here'''
    return Interface.normalize(port)

class ShowInterface(NXCLI):
    def __init__ (self, ifname):
        # acquire the output of "show interface %ifname | xml"
        super(ShowInterface, self).__init__('show interface %s | xml' % ifname, False)

    def parse_specific(self):
        # parse the XML
        elements = self.get_xml_dom_from_cli_output (self.raw_output)
        # loop through the leaves of the XML tree and populate the dictionary
        for element in elements.getiterator():
            # if the element is a leaf
            if not element.getchildren():
                # store it in the dictionary sans the XML namespace prefix
                ret = self.key_value_xml_parser (element)
                if ret:
                    key, value = ret
                    self.__dict__[key] = value



class Interface(object):
    _pat = None
    _interfaces, _Interfaces = None, {}


    @classmethod
    def interfaces(cls, refresh=False):
        '''Returns the list of interfaces on the switch'''
        if cls._interfaces is None or refresh:
            x = nxcli('show interface | exclude "^ " | exclude "^admin state" | include " is " ')
            cls._interfaces = [i.split(' ')[0] for i in x[1].split('\n'
                ) if i ]
        return cls._interfaces


    @classmethod
    def parsed_if(cls, intf):
        if cls._pat is None:
            cls._pat = re.compile('(\D+)(\d.*)')
        m = cls._pat.match(intf)
        if m:
            return m.groups()[0].lower(), map(eval, m.groups()[1].split('/'))
        raise ValueError, 'interface "%s" is not valid' % intf


    @classmethod
    def normalize(cls, intf):
        type, dlist = cls.parsed_if(intf)
        for x in cls.interfaces():
            t, d = cls.parsed_if(x)
            if dlist == d and t.startswith(type):
                return x
        for x in cls.interfaces(True):
            t, d = cls.parsed_if(x)
            if dlist == d and t.startswith(type):
                return x
        raise ValueError, 'interface "%s" is not valid' % intf


    def __new__(cls, intf):
        name = cls.normalize(intf)
        if name not in cls._Interfaces:
            cls._Interfaces[name] = super(Interface, cls).__new__(cls)
            cls._Interfaces[name].name = name
            cls._Interfaces[name]._config = None
            cls._Interfaces[name]._cfgHistory = []
            cls._Interfaces[name].config(True)
            cls._Interfaces[name]._show_obj = ShowInterface(name)
        return cls._Interfaces[name]


    def __del__(cls):
        ''' system shared obj, dont delete '''
        pass


    def __init__(self, intf):
        self._newCfg = None


    def config(self, refresh = False):
        if self._config is None or refresh:
            s, o = nxcli('show runn interface %s' % self.name)
            if s == 0:
                self._config = o
            else:
                raise RuntimeError, \
                    'Cant extract config for interface %s\nError:\n%s\n%s' % (
                            self.name, '-' * 6, o)
        return self._config


    def show (self, key=None):
        self._show_obj.rerun ()
        if not key:
            return self._show_obj
        return getattr (self._show_obj, key)


    def _if_cfg(self, cfg):
        if self._newCfg is None:
            self._newCfg = '''configure term ; interface %s ''' % self.name
        self._newCfg += ' ; ' + cfg


    def set_mode(self, mode='access'):
        if mode.lower() not in ['access', 'trunk']:
            raise ValueError, 'switchport mode %s is unknown' % mode
        self._if_cfg('switchport mode %s' % mode)
        return self.apply_config ()


    def set_switchport(self, **kwargs):
        self._if_cfg(NXCLI._add_no_if_present('switchport', kwargs))
        return self.apply_config()


    def set_trunk_allowed_vlans(self, vlans=[]):
        if str(vlans) == 'all':
            self._if_cfg('switchport trunk allowed vlan all')
        else:
            self._if_cfg('switchport trunk allowed vlan %s' % ','.join(map (str, vlans)))
        return self.apply_config ()


    def set_trunk_native_vlan(self, vlan=1):
        self._if_cfg('switchport trunk native vlan %d' % vlan)
        return self.apply_config ()


    def set_access_vlan(self, vlan=1):
        self._if_cfg('switchport access vlan %d' % vlan)
        return self.apply_config ()


    def show_new_config(self):
        return self._newCfg


    def apply_config(self):
        newCfg = self._newCfg
        self._newCfg = None
        o,e,s = nxos_utils.runVshCmdEx(newCfg)
        if s:
            if e:
                print e
            else:
                print o
        self.config(True)
        self._cfgHistory.append((datetime.datetime.now(), newCfg))
        return s == 0


    def set_description(self, d=None):
        if d:
            self._if_cfg('description %s' % d)
        else:
            self._if_cfg('no description')
        return self.apply_config ()


    def set_state(self, s='up'):
        if s.lower() in ['up', 'no shut', 'noshut']:
            self._if_cfg('no shut')
        else:
            self._if_cfg('shut')
        return self.apply_config ()


    def _set_ipaddress(self, ip_address=None, mask=None, secondary=None, delete=None):
        #  set the ip (v4/v6)  address on an interface.  For now only for internal use.
        if delete:
            ip_cfg = "no "

        if ip_address :
            if '/' in ip_address or not mask:
                self.ip_address = ipaddress.ip_interface(ip_address)
            else:
                self.ip_address = ipaddress.ip_interface(ip_address + '/' + mask)

            if self.ip_address.version == 4:
                ip_cfg = "ip address " + str(self.ip_address)
            elif self.ip_address.version == 6:
                ip_cfg = "ipv6 address " + str(self.ip_address)

            if secondary:
                ip_cfg = " secondary"            
            self._if_cfg(ip_cfg)
        else:
            raise pexpect.ExceptionPexpect("IP Address required.")

        return self.apply_config ()



