# Copyright (C) 2013 Cisco Systems Inc.
# All rights reserved
import socket

import _cisco

from .vrf import VRF


class CiscoSocket(socket.socket):
    '''
    Extends the socket.socket class in order to provide a way to set/get the VRF    associated with a socket. The default VRF for a CiscoSocket is 'management' 
    (2).
    '''

    def get_vrf(self):
        '''
        Gets the VRF associated with a CiscoSocket. 

        Arguments: None

        Returns: VRF name as a string

        Example:
            s = CiscoSocket(socket.AF_INET, socket.SOCK_STREAM)
            s.get_vrf()
        
        '''

        try:
            return VRF.get_vrf_name_by_id(self.vrf)
        except AttributeError:
            self.vrf = 2
            return VRF.get_vrf_name_by_id(self.vrf)


    def set_vrf(self, vrf):
        '''
        Sets the VRF on a CiscoSocket.  The default VRF for a CiscoSocket is 
        'management' (2).

        Arguments:
            vrf: VRF name (string) or the VRF ID (int).

        Returns: True on success

        Example:
            a. s = CiscoSocket(socket.AF_INET, socket.SOCK_STREAM)
               s.set_vrf(3)
            b. s = CiscoSocket(socket.AF_INET, socket.SOCK_STREAM)
               s.set_vrf('floor1')
        
        '''
              
        if type(vrf) is str:
            vrf = VRF.get_vrf_id_by_name(vrf)

        ret = _cisco.set_vrf(self.family, self.fileno(), vrf)
        if ret == 0:
            self.vrf = vrf
        else:
            raise ValueError, 'set_vrf failed and returned %d' % ret

        return True



