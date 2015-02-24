# Copyright (C) 2013 Cisco Systems Inc.
# All rights reserved
import os
import _cisco



def md5sum(filename, keep=False):
    '''
    Calculate the MD5 checksum on a file
    
    Arguments:
        filename: A string representing the filename (e.g. 'bootflash:file.txt',
            '/bootflash/file.txt', 'file.txt')
        keep: A boolean, set to True to save the MD5 checksum in a file. It will
            get saved as <filename>.md5. Default value is False.

    Returns: 
        On success, MD5 checksum as a string

    '''
    
    if not filename.startswith('/bootflash'):
        if filename.startswith('bootflash:'):
            filename = filename.replace('bootflash:', '/bootflash/')
        elif not filename.startswith('/'):
            filename = '/bootflash/%s' % filename
        else:
            raise ValueError, 'File must reside in /bootflash'
    
    #try opening the file to make sure it exists, it will throw an IOError if
    #it doesn't exist
    f = open(filename, 'r')
    f.close()

    ret_val = _cisco.cisco_md5sum(filename)
    if ret_val == -1:
        print "md5 checksum calculation failed."
        return

    f = open('%s.md5' % filename, 'r')
    line = f.readline()
    f.close()
    if not keep:
        os.remove('%s.md5' % filename)
    return line.split()[0]




