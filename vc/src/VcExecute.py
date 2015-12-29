#-*- coding:utf-8 -*-

import subprocess, re
import threading
from Queue import Queue
from time import sleep

from VcEventPipe import *

class VcTask:
    ''' 一个任务，对应一个命令组。'''
    
    def __init__(self, work_dir, platform, vc_cmd_grp):
        self.work_dir = work_dir            # 工作目录路径
        self.platform = platform            # 平台
        self.vc_cmd_grp = vc_cmd_grp    # 需要执行的命令组

class VcExecute:
    
    ''' 执行任务管理
    每个任务队列都是独立运行的，相互之间不影响（可能因为机器运行的速度，而相互之间错开)。
    '''
    
    ''' 实现机制
    1，每个任务队列都启动一个执行线程执行。
    '''
    
    my_instance = None
    
    @staticmethod
    def instance():
        if VcExecute.my_instance is None:
            VcExecute.my_instance = VcExecute()
            
        return VcExecute.my_instance
    
    @staticmethod
    def add_task(work_dir, platform, vc_cmd_group):
        # 添加一个任务。
        VcExecute.instance()._add_task(work_dir, platform, vc_cmd_group)
        
    @staticmethod
    def terminate_all_tasks():
        # 终止当前所有的任务。 TODO: 没有实现
        VcExecute.instance()._terminate_all_task()
        
    @staticmethod
    def reset_state():
        # 重设当前的状态。TODO: 没有实现
        VcExecute.instance()._destroy()

    def __init__(self):
        # 任务队列(内部类型 VcTask)
        self.is_continue = True
        self.task_queue = Queue(256)
        
    def _add_task(self, work_dir, platform, vc_cmd_grp):
        ''' 加入新任务。'''
        
        vc_task = VcTask(work_dir, platform, vc_cmd_grp)
        
        # 启动一个新的线程，用来执行这个命令组。
        thrd_execute = threading.Thread(target=self._thread_execute_cmd_grp, args=(vc_task,))
        thrd_execute.start()

    def _thread_execute_cmd_grp(self, vc_task):
        # 执行一个命令组
        for vc_cmd in vc_task.vc_cmd_grp.commands:
            
            # 没有被选中，就跳过。
            if not vc_cmd.is_selected:
                continue
            
            is_ok = self._execute_cmd(vc_task, vc_cmd)
            
            # 如果此命令执行不成功，则取消整个命令组的执行，发出“取消“信号。
            if not is_ok:
                VcEventPipe.send_event(VcEventPipe.EVENT_CMD_GRP_CANCEL, vc_task.vc_cmd_grp)
                return
        
        VcEventPipe.send_event(VcEventPipe.EVENT_CMD_GRP_FINISH, vc_task.vc_cmd_grp)
        
    def _execute_cmd(self, vc_task, vc_cmd):
        # 执行一个命令

        # - 发送命令开始信号
        VcEventPipe.send_event(VcEventPipe.EVENT_CMD_START, vc_cmd)
        
        vc_cmd.register_output()
        
        command = ". ./set_env -z %s && %s" % (vc_task.platform, vc_cmd.get_exe_command())
        print "execute %s" % (command)
        p = subprocess.Popen(command, shell=True, executable="/bin/bash", 
                             cwd = vc_task.work_dir,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        
        # 直到命令结束。
        obj_result = None
        while True:
            line = p.stdout.readline()
            self._parse_result(vc_task.vc_cmd_grp, vc_cmd, line)
            
            # - 发送命令进度信号
            VcEventPipe.send_event(VcEventPipe.EVENT_CMD_PROCESS, vc_cmd, 50) # TODO:暂时50
            
            obj_result = p.poll()
            if obj_result is not None:
                print "process is end."
                break
            
        vc_cmd.unregister_output()
        
        result = obj_result
        if result == 0:
            is_ok = True
        else:
            is_ok = False
        
        # - 发送命令结束信号
        VcEventPipe.send_event(VcEventPipe.EVENT_CMD_FINISH, vc_cmd, is_ok, result)
        
        return is_ok

    def _parse_result(self, vc_cmd_grp, vc_cmd, text):
        # 发送异步命令，在主线程内调用，更新画面
        #print "send " + text,
        VcEventPipe.send_event(VcEventPipe.EVENT_CMD_OUTPUT, vc_cmd_grp, vc_cmd, text)

    def _terminate_all_task(self):
        pass

    def _destroy(self):
        self._terminate_all_task()
        self.is_continue = False
        