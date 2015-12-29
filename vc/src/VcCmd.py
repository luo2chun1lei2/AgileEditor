#-*- coding:utf-8 -*-

# 数据模型。
# 1，数据保存为一个XML文件。
# 2，采用elementTree管理这个XML文件。
# 3，CommandGroupList -> CommandGroup -> Command
# 3.1，Command包含命令的内容。
# 3.2，CommandGroup包括内部命令列表，以及对应的参数。
# 3.3，CommandGroupList包括目前所有的命令组。

import os, os.path

from VcCmdTemplate import *
from VcEventPipe import *
from xml.etree.ElementTree import *

class VcState:
    ''' 命令运行的情况。'''
    def __init__(self):
        pass

class VcCmd:
    ''' 命令动作
    包含该动作的执行情况。
    '''

    def __init__(self, content, is_selected):
        
        # 命令的内容
        self.content = content
        # 命令补充的部分（比如参数）
        self.param = ""
        
        #--------------------------
        # 下面是运行的情况。
        
        # 命令是否被选中
        self.is_selected = is_selected
        
        # 命令当前的运行状态(-1:是错误，0：没有开始，~100：正在进行中，100：完成)
        self.process = 0
        
        # 日志缓冲在一个临时文件中，这样可以适应大数据和永久保存的需要。
        self.log_file = os.tmpfile()
        
    def get_exe_command(self):
        ''' 取得可以执行的命令 '''
        return self.content + " " + self.param
    
    def get_log(self):
        text = ""
        
        self.log_file.seek(0)
        for line in self.log_file:
            text += line
            
        return text
    
    def get_content(self):
        ''' 取得设定的名字 '''
        return self.content
    
    def set_content(self, text):
        self.content = text
    
    def set_param(self, text):
        self.param = text
        
    def get_param(self):
        return self.param
    
    def set_process(self, process):
        self.process = process
        
    def get_process(self):
        return self.process
        
    def register_output(self):
        ''' 连接命令输出事件 '''
        VcEventPipe.register_event(VcEventPipe.EVENT_CMD_OUTPUT, self.on_command_add_output);
                                                        
    def unregister_output(self):
        ''' 注销命令输出事件 '''
        VcEventPipe.unregister_event(VcEventPipe.EVENT_CMD_OUTPUT, self.on_command_add_output);

    def on_command_add_output(self, vc_cmd_grp, vc_cmd, text):
        
        if self is not vc_cmd:
            return
        
        self.log_file.write(text)
        
        VcEventPipe.send_event(VcEventPipe.EVENT_LOG_APPEND_TEXT, vc_cmd, text)
        
    def reset_state(self):
        ''' 重置所有的处理情况。'''
        
        self.process = 0
        
        self.log_file.seek(0)
        self.log_file.truncate()
        
    def close(self):
        ''' 释放这个命令。'''
        if self.log_file:
            self.log_file.close()
            self.log_file = None

class VcCmdGroup:
    ''' 命令组
    key string ID号，唯一
    commands [VcCmd] 命令的数组
    process int 当前执行情况，0：还没有执行，100：执行完成，中间值：正在执行，-1：错误。
    '''
    
    def __init__(self, key):
        self.key = key
        self.commands = []
        self.process = 0
        
    def get_key(self):
        return self.key
    
    def set_key(self, key):
        self.key = key
    
    def add_cmd(self, cmd):
        self.commands.append(cmd)

    def get_process(self):
        l = len(self.commands)
        if l == 0:
            one_len = 0
        else:
            one_len = 100 / l 
        
        process = 0
        
        for cmd in self.commands:
            if cmd.process == -1: # 执行错误
                process = -1
                break
            elif cmd.process == 0:    # 还没有开始
                break
            elif cmd.process == 100:    # 已经结束
                self.process += one_len
            elif 0 < cmd.process and cmd.process <100 :    # 正在进行中。
                self.process += cmd.process * one_len / 100
                break
            else:   # 非法数据
                process = -1
                break
                
        return process
        
    def reset_state(self):
        for vc_cmd in self.commands:
            vc_cmd.reset_state()
        
class ReadCmdGroupList:
    # 读取命令 TODO:暂缓，首先处理数据结构本身的问题。
    def __init__(self):
        pass

    def read(self, path):
        ''' 从指定的文件中读取命令列表，返回一个[VcCmdGroup] '''
        pass
    
    def write(self, cmdgroups, path):
        ''' 将命令组列表，保存到指定的文件中。'''
        pass
    
class VcCmdGroupMng:
    ''' 管理命令组
    cmd_groups [VcCmdGroup]:命令的数组
    '''
    
    my_instance = None
    
    @staticmethod
    def instance():
        if VcCmdGroupMng.my_instance is None:
            VcCmdGroupMng.my_instance = VcCmdGroupMng()
        
        return VcCmdGroupMng.my_instance
    
    def __init__(self):
        self.cmd_groups = []
        self._read_data()
        
    def _read_data(self):
        ''' 读取目前的命令 '''
        
        cmd_grp = VcCmdGroup("soter and its")
        cmd_grp.add_cmd(VcCmd("soter_init", False))
        cmd_grp.add_cmd(VcCmd("soter_clean", False))
        cmd_grp.add_cmd(VcCmd("soter_setup", False))
        cmd_grp.add_cmd(VcCmd("soter_make", True))
        cmd_grp.add_cmd(VcCmd("soter_make_bin", True))
        cmd_grp.add_cmd(VcCmd("soter_install_dev", True))
        cmd_grp.add_cmd(VcCmd("its_init", False))
        cmd_grp.add_cmd(VcCmd("its_clean", False))
        cmd_grp.add_cmd(VcCmd("its_make", True))
        cmd_grp.add_cmd(VcCmd("its_install_dev", False))
        cmd_grp.add_cmd(VcCmd("its_install_bin", True))
        cmd_grp.add_cmd(VcCmd("run_emu", True))
        self.cmd_groups.append(cmd_grp)
        
        cmd_grp = VcCmdGroup("its_run")
        cmd_grp.add_cmd(VcCmd("its_run_dummytee", True))
        self.cmd_groups.append(cmd_grp)
        
        cmd_grp = VcCmdGroup("teei_test")
        cmd_grp.add_cmd(VcCmd("test_ta_init", False))
        cmd_grp.add_cmd(VcCmd("test_ta_clean", False))
        cmd_grp.add_cmd(VcCmd("test_ta_make", True))
        cmd_grp.add_cmd(VcCmd("test_ta_install_bin", True))
        self.cmd_groups.append(cmd_grp)
    
    def _find(self, key):
        for grp in self.cmd_groups:
            if grp.get_key() == key:
                return grp
            
        return None
    
    @staticmethod
    def find(key):
        return VcCmdGroupMng.instance()._find(key)

class VcPlatform:
    
    my_instance = None
    
    # Workshop的平台管理
    def __init__(self):
        pass
    
    @staticmethod
    def instance():
        if VcPlatform.my_instance is None:
            VcPlatform.my_instance = VcPlatform()
        return VcPlatform.my_instance
    
    def init(self, workshop_dir):
        self.workshop_dir = workshop_dir
    
    def get_platform_list(self):
        # 取得平台名字的列表
        path = self.workshop_dir + "/tools/zhtools/configs"
        
        platforms = []
        
        if not os.path.isdir(path):
            return platforms
        
        files = os.listdir(path)
        for f in files:
            if f == 'setenv.sh':
                continue
            platforms.append(os.path.basename(f))
        
        return platforms
