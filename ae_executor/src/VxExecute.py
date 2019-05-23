#-*- coding:utf-8 -*-

import subprocess, re, os
import threading
from Queue import Queue
from time import sleep

from gi.repository import Gdk, GLib
from VxSourceCmd import *

class VxExecute:
    
    my_instance = None
    
    @staticmethod
    def instance():
        if VxExecute.my_instance is None:
            VxExecute.my_instance = VxExecute()
            
        return VxExecute.my_instance
    
    def __init__(self):
        pass
    
    @staticmethod
    def execute_cmd(vx_source_cmd):
        return VxExecute.instance()._execute_cmd(vx_source_cmd)
    
    def _execute_cmd(self, vx_source_cmd):    
        
        source = vx_source_cmd.source
        command = vx_source_cmd.command

        work_dir = os.path.expanduser("~/")
        
        p = subprocess.Popen(command, shell=True, executable="/bin/bash",
                             cwd = work_dir,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
        p.stdin.write(source)
        
        (stdoutput, erroutput) = p.communicate()
        returncode = p.returncode
        
        p.stdin.close()
        
        return self._parse_result(returncode, stdoutput, erroutput)

    def _parse_result(self, returncode, text, error):
        if returncode == 0:
            return returncode, VxSourceCmd(text, None)
        else:
            return returncode, error
