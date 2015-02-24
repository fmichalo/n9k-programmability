# Copyright (C) 2013 Cisco Systems Inc.
# All rights reserved
import ipaddress
from abc import ABCMeta
import re

from .nxcli import NXCLI
from .key import Key
from .section_parser import SectionParser


class ShACL (NXCLI):
    def __init__ (self, proto, name):
        self._name = name
        super (ShACL, self).__init__ ('show %s access-lists %s' % (
            proto, name))
    
    def parse_specific(self):
        k = Key (start=r"^IP access list %s" % self._name)
        spl = SectionParser (self.processed_output, k)
        if spl:
            self.list = [x.strip() for x in spl.sections[0:-1] if x]
        else:
            self.list = []

    def ACEs (self):
        for l in self.list:
            yield l


class ACL (object):
    '''
    A base ACL object, should use IPv4ACL or IPv6ACL to configure each 
    type of ACL appropriately.
    '''
    
    __metaclass__ = ABCMeta
    ace_pat = re.compile (r'^\d+')
    def __init__ (self, proto, name):
        self.proto = proto
        self.name = name
        self._shacl = ShACL (self.proto, self.name)
        #self.load ()
        self.create ()


    def load (self):
        for ace in self._shacl.ACEs ():
            if self.ace_pat.match (ace):
                #self.add_ace_from_string (ace)
                pass
            else:
                #self.add_flags_from_string (ace)
                pass


    def show (self):
        '''
        Show the currently configured entries in this ACL.
        
        Arguments: None

        Returns: Outputs the ACL entries
        '''

        self._shacl.rerun ()
        print self._shacl.get_output ()

    
    def create(self):
        '''
        Create the ACL associated with this object.

        Arguments: None

        Returns: True on success
        '''

        return NXCLI._run_cfg('%s access-list %s' % (self.proto, self.name))

    def delete(self):
        '''
        Delete the ACL associated with this object.

        Arguments: None

        Returns: True on success
        '''

        return NXCLI._run_cfg('no %s access-list %s' % (self.proto, self.name))


    def _add_acl_cfg (self, cfg):
        return NXCLI._run_cfg ('%s access-list %s ; %s' % (
            self.proto, self.name, cfg))


    def _sequence (self, kwargs):
        return NXCLI._read_arg_from_dict (kwargs, 'sequence', '%',
                {int:'sequence >= 1 and sequence <= 4294967295'})


    def set_per_entry_statistic (self, **kwargs):
        '''
        Set the per-entry statistics this ACL. To remove this configuration, set 
        the optional 'no' argument to True.

        Arguments:
            None
        
        Optional Arguments:
            no: A boolean, set to True to remove the per-entry statistics.

        Returns: True on success

        '''
        return self._add_acl_cfg (CLI._add_no_if_present (
            'statistics per-entry', kwargs))


    def set_remark (self, remark, **kwargs):
        '''
        Set a remark. To remove a remark, set the optional 'no' argument to 
        True.

        Arguments:
            remark: a string containing the remark
        
        Optional Arguments:
            no: A boolean, set to True to remove a particular remark.
            sequence: an Integer sequence # where the remark will be placed

        Returns: True on success

        '''
        cmd = NXCLI._add_no_if_present(self._sequence(kwargs) + ' remark', 
                kwargs)
        cmd += NXCLI._read_arg(remark, 'remark', ' %', {str: 
            'len(remark) >= 1 and len(remark) <= 100'})
        return self._add_acl_cfg(cmd)


    @staticmethod
    def _parse_ip_for_acl_and_create_str(ip, version=4):
        parsed_ip = None
        cmd = ""

        try:
            parsed_ip = ipaddress.ip_address(ip, version)
            cmd += ' host %s' % str(parsed_ip)
        except (ValueError):
            try:
                parsed_ip = ipaddress.ip_network(ip, version, strict = False)
                cmd += ' %s' % str(parsed_ip)
            except (ValueError):
                if ip == 'any':
                    cmd += ' any'
                else:
                    ips = ip.split('/')
                    if len(ips) > 1:
                        addr = ips[0]
                        wildcard_bits = ips[1]
                        parsed_ip = ipaddress.ip_address(addr, version)
                        if parsed_ip:
                            cmd += ' %s %s' % (str(parsed_ip), wildcard_bits)
                        else:
                            raise ValueError, 'Bad address'
                    else:
                        raise ValueError, 'Bad address'

        return cmd
       
       
    def _permit_or_deny_base(self, type, protocol, source, destination, kwargs):
        
        cmd = NXCLI._add_no_if_present('%s %s' % (self._sequence(kwargs), type), 
                kwargs)
       
        if (isinstance(self, IPv4ACL)):
            cmd += NXCLI._read_arg(protocol, 'protocol', ' %', {int: 
                'protocol >= 0 and protocol <= 255', str: 
                'protocol in ("ahp", "eigrp", "esp", "gre", "icmp", "igmp", \
                        "ip", "nos", "ospf", "pcp", "pim", "tcp", "udp")'})
            version = 4
        elif (isinstance(self, IPv6ACL)):
            cmd += NXCLI._read_arg(protocol, 'protocol', ' %', {int: 
                'protocol >= 0 and protocol <= 255', str: 
                'protocol in ("icmp", "ipv6", "sctp", "tcp", "udp")'})
            version = 6
        else:
            version = None

        cmd += ACL._parse_ip_for_acl_and_create_str(source, version)
        cmd += ACL._parse_ip_for_acl_and_create_str(destination, version)
        
        if kwargs.has_key('dscp') and kwargs.has_key('precedence'):
            raise AttributeError, 'Cannot specify both dscp and precedence'

        cmd += NXCLI._read_arg_from_dict(kwargs, 'dscp', ' dscp %', 
            {str: 'dscp in ("af11", "af12", "af13", "af21", "af22", "af23", \
            "af31", "af32", "af33", "af41", "af42", "af43", "cs1", "cs2", \
            "cs3", "cs4", "cs5", "cs6", "cs7", "default", "ef")', int: 
            'dscp >= 0 and dscp <= 63'})
        
        if (isinstance(self, IPv4ACL)):
            cmd += NXCLI._read_arg_from_dict(kwargs, 'precedence', ' precedence %',
                {str: 'precedence in ("critical", "flash", "flash-override", \
                        "immediate", "internet", "network", "priority", "routine")', 
                        int: 'precedence >= 0 and precedence <= 7'})
        
        cmd += NXCLI._read_arg_from_dict(kwargs, 'fragments', ' fragments',
            {bool: None})
        
        return self._add_acl_cfg(cmd)

       
    def delete_entry(self, sequence):
        '''
        Delete a particular entry in this ACL by specifying the sequence number.

        Arguments:
            sequence: An integer ranging from <1-4294967295>.

        Returns: True on success
        '''

        return self._add_acl_cfg('no ' + str(sequence))



class IPv4ACL (ACL):
    '''
    Use this class to configure the IPv4 ACL
    '''
    def __init__ (self, name):
        super (IPv4ACL, self).__init__ ('ip', name)
    
    
    def permit(self, protocol, source, destination, **kwargs):
        '''
        Specify packets to forward. To stop forwarding particular packet types 
        set the optional 'no' argument to True.

        Arguments:
            protocol: An integer ranging from <0-255> representing the protocol
                number, or a string representing the protocol name.
            source: A string representing the source ip address or network in 
                either CIDR notation or dotted quad. E.g. '192.0.2.0', 
                '192.0.2.0/24', '192.0.2.0/255.255.255.0'. For a network can 
                also specify wildcard bits. E.g. '192.0.2.0/255.0.7.255'
            destination: A string representing the source ip address or network in 
                either CIDR notation or dotted quad. E.g. '192.0.2.0', 
                '192.0.2.0/24', '192.0.2.0/255.255.255.0'. For a network can 
                also specify wildcard bits. E.g. '192.0.2.0/255.0.7.255'

        Optional Arguments:
            sequence: an integer ranging from <1-4294967295> where this rule 
                will be placed.
            dscp: An integer ranging from <0-63> or a string represting the type 
                of dscp. Use this to match packets with a particular dscp value.
            fragments: A boolean, set to True to check non-initial fragments.
            precedence: An integer ranging from <0-7> or a string representing 
                the precedence type. Use this to match packets with a particular
                precedence value.
            no: A boolean, set to True to stop forwarding particular packet 
                types.

        '''

        return self._permit_or_deny_base('permit', protocol, source, 
                destination, kwargs)


    def deny(self, protocol, source, destination, **kwargs):
        '''
        Specify packets to reject. To stop rejecting particular packet types 
        set the optional 'no' argument to True.

        Arguments:
            protocol: An integer ranging from <0-255> representing the protocol
                number, or a string representing the protocol name.
            source: A string representing the source ip address or network in 
                either CIDR notation or dotted quad. E.g. '192.0.2.0', 
                '192.0.2.0/24', '192.0.2.0/255.255.255.0'. For a network can 
                also specify wildcard bits. E.g. '192.0.2.0/255.0.7.255'
            destination: A string representing the source ip address or network in 
                either CIDR notation or dotted quad. E.g. '192.0.2.0', 
                '192.0.2.0/24', '192.0.2.0/255.255.255.0'. For a network can 
                also specify wildcard bits. E.g. '192.0.2.0/255.0.7.255'

        Optional Arguments:
            sequence: an integer ranging from <1-4294967295> where this rule 
                will be placed.
            dscp: An integer ranging from <0-63> or a string represting the type 
                of dscp. Use this to match packets with a particular dscp value.
            fragments: A boolean, set to True to check non-initial fragments.
            precedence: An integer ranging from <0-7> or a string representing 
                the precedence type. Use this to match packets with a particular
                precedence value.
            no: A boolean, set to True to stop rejecting particular packet 
                types.

        Returns: True on Success

        '''

        return self._permit_or_deny_base('deny', protocol, source, 
                destination, kwargs)



class IPv6ACL (ACL):
    '''
    Use this class to configure the IPv6 ACL
    '''
    def __init__ (self, name):
        super (IPv6ACL, self).__init__ ('ipv6', name)


    def permit(self, protocol, source, destination, **kwargs):
        '''
        Specify packets to forward. To stop forwarding particular packet types 
        set the optional 'no' argument to True.

        Arguments:
            protocol: An integer ranging from <0-255> representing the protocol
                number, or a string representing the protocol name.
            source: A string representing the source ip network in CIDR 
                notation. E.g. '1:1::1:1/32'. 
            destination: A string representing the destination ip network in 
                CIDR notation. E.g. '1:1::1:1/32'. 

        Optional Arguments:
            sequence: an integer ranging from <1-4294967295> where this rule 
                will be placed.
            dscp: An integer ranging from <0-63> or a string represting the type 
                of dscp. Use this to match packets with a particular dscp value.
            fragments: A boolean, set to True to check non-initial fragments.
            no: A boolean, set to True to stop forwarding particular packet 
                types.

        '''

        return self._permit_or_deny_base('permit', protocol, source, 
                destination, kwargs)


    def deny(self, protocol, source, destination, **kwargs):
        '''
        Specify packets to reject. To stop rejecting particular packet types 
        set the optional 'no' argument to True.

        Arguments:
            protocol: An integer ranging from <0-255> representing the protocol
                number, or a string representing the protocol name.
            source: A string representing the source ip network in CIDR 
                notation. E.g. '1:1::1:1/32'. 
            destination: A string representing the destination ip network in 
                CIDR notation. E.g. '1:1::1:1/32'. 

        Optional Arguments:
            sequence: an integer ranging from <1-4294967295> where this rule 
                will be placed.
            dscp: An integer ranging from <0-63> or a string represting the type 
                of dscp. Use this to match packets with a particular dscp value.
            fragments: A boolean, set to True to check non-initial fragments.
            no: A boolean, set to True to stop rejecting particular packet 
                types.

        Returns: True on Success

        '''

        return self._permit_or_deny_base('deny', protocol, source, 
                destination, kwargs)




