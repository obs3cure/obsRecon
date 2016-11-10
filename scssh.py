#!/usr/bin/python
# -*- coding: utf-8 -*-
import pexpect

PROMPT = ['# ', '>>> ', '> ','\$ ']

def send_command(child, cmd):
    child.sendline(cmd)
    child.expect(PROMPT)
    print child.before

def connectsh(user, host, password):
    ssh_newkey = 'Are you sure you want to continue connecting'
    connStr = 'ssh ' + user + '@' + host
    child = pexpect.spawn(connStr)
    ret = child.expect([pexpect.TIMEOUT, ssh_newkey,\
                        '[P|p]assword:'],timeout=1)
    
    if ret == 0:
        print '[-] Error Connecting'
        return
    
    if ret == 1:
        child.sendline('yes')
        ret = child.expect([pexpect.TIMEOUT, \
                            '[P|p]assword:'],timeout=1)
        if ret == 0:
            print '[-] Error Connecting'
            return False
    
    child.sendline(password)
    child.expect(PROMPT)
   # send_command(child, 'exit')	
    return True
