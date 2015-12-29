#-*- coding:utf-8 -*-

''' 画面：显示多页
1, 可以添加、删除、移动页 
'''

import os, sys
from collections import OrderedDict
from gi.repository import Gtk, Gdk, GtkSource, GLib, Pango, Gio

from VcCmd import *
from ViewCmdGroup import *
from ViewLog import *
from VcExecute import *

class PageInfo:
    ''' 一个页的信息
    cmdList ViewCmdGroup 源代码的编辑器控件
    ide_file ModelFile 编辑的文件
    '''
    
    # 编辑器当前的状态。
    (
     PAGE_STATUS_NO_MODIFIED, # 没有被修改
     PAGE_STATUS_MODIFIED,    # 被修改了
     ) = range(2)
    
    def __init__(self, command_name):
        self.command_name = command_name
        
    def get_name(self):
        return self.command_name
        
class ViewPage:
    ''' 对等于一个Page的控件。'''
    def __init__(self, vc_cmd_grp):
        
        ''' 从上到下：设定控件、命令列表、执行控件, 日志 '''
        self.vc_cmd_grp = vc_cmd_grp
        
        self.panedCmdAndLog = Gtk.Paned.new(Gtk.Orientation.VERTICAL)
        #panedCmdAndLog.set_position(800);
        
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # 平台名字
        self.cmbPlatform = Gtk.ComboBoxText.new()
        self.cmbPlatform.set_border_width(5)
        self._init_platform_combo(self.cmbPlatform)
        self.vbox.pack_start(self.cmbPlatform, False, False, 0)
        
        # 命令组的命令列表
        self.viewCmdGroup = ViewCmdGroup(vc_cmd_grp)
        self.cmdList = self.viewCmdGroup.treeview
        self.scrolledCtrl = self.viewCmdGroup.scrolledCtrl
        
        self.vbox.pack_start(self.scrolledCtrl, False, True, 0)
        
        self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        # 执行按钮
        self.btnExecute = Gtk.Button.new_with_label("执行")
        self.btnExecute.connect("clicked", self.on_execute_clicked)
        
        self.hbox.pack_start(self.btnExecute, False, False, 0)
        
        # 最新日志
        self.chkLatestLog = Gtk.CheckButton.new_with_label("滚动到最新")
        self.chkLatestLog.set_active(True)
        self.chkLatestLog.connect("toggled", self.on_lastest_log_toggled)
        
        self.hbox.pack_start(self.chkLatestLog, False, False, 0)
        
        # 最新命令
        self.chkLatestCmd = Gtk.CheckButton.new_with_label("跟踪最新命令")
        self.chkLatestCmd.set_active(True)
        self.chkLatestCmd.connect("toggled", self.on_lastest_cmd_toggled)
        
        self.hbox.pack_start(self.chkLatestCmd, False, False, 0)
        
        self.vbox.pack_start(self.hbox, False, False, 0)
        
        self.panedCmdAndLog.pack1(self.vbox, resize=True, shrink=True)
        
        # 日志
        self.viewLog = ViewLog(vc_cmd_grp)
        self.viewConsole = self.viewLog.view
        self.panedCmdAndLog.pack2(self.viewConsole, resize=True, shrink=True)
        
        VcEventPipe.register_event(VcEventPipe.EVENT_LOG_SET, self.sm_set_log)
        
    def on_close(self):
        # 当这个控件被关闭时。
        VcEventPipe.unregister_event(VcEventPipe.EVENT_LOG_SET, self.sm_set_log)
        
        self.viewLog.unregister()
        self.viewCmdGroup.unregister()
        
    def layout(self):
        self.cmbPlatform.show()
        
        self.cmdList.show()
        self.scrolledCtrl.show()
        
        self.btnExecute.show()
        self.chkLatestLog.show()
        self.chkLatestCmd.show()
        self.hbox.show()
        
        self.vbox.show()
        
        self.viewLog.layout()
        self.panedCmdAndLog.show()
        
    #########################
    # 跟踪最新的命令，不滚动/滚动
    # 不跟踪最新的命令，不滚动/滚动

    def on_lastest_log_toggled(self, checkButton):
        # 显示当前命令的最新输出，
        # 相反，则是不滚动，即使是调用其他命令也不再跳动。
        active = checkButton.get_active()
        self.viewLog.set_scrollable(active)

    def on_lastest_cmd_toggled(self, checkButton):
        # 显示最新命令的日志。
        # 相反，则停留在此命令的日志中，不过命令
        active = checkButton.get_active()
        self.viewLog.set_show_new_cmd_log(active)
    
    def on_execute_clicked(self, button):
        ''' 执行命令。'''
        
        platform = self.cmbPlatform.get_active_text()
        work_dir = os.path.expanduser("~/workshop")
        
        # 禁止编辑
        self.viewCmdGroup.freeze()

        # 更新当前状态。
        list_store = self.cmdList.get_model()
        iter_ = list_store.get_iter_first()
        while iter_:
            vc_cmd = list_store.get_value(iter_, ViewCmdGroup.COLUMN_CMD_OBJ).cmd
            
            vc_cmd.reset_state()
            #is_selected = vc_cmd.is_selected
            # 因为修改了命令组中命令的状态，所以需要更新画面
            self.viewCmdGroup.refresh(iter_, vc_cmd)
             
            iter_ = list_store.iter_next(iter_)
            
        # 执行命令
        VcExecute.add_task(work_dir, platform, self.viewCmdGroup.vc_cmd_grp)
            
    def _init_platform_combo(self, combo):
        # 初始化平台列表，缺省选择"emu"
        combo.set_title("平台")
        
        # 将combo中初始化平台的名字
        active_index = 0
        platforms = VcPlatform.instance().get_platform_list()
        for p in platforms:
            if p == "emu":
                active_index = platforms.index(p)
            combo.append(p, p)
            
        combo.set_active(active_index)
        
    def sm_set_log(self, vc_cmd):
        
        # 如果命令不是这个命令组中的，就退出
        if vc_cmd not in self.vc_cmd_grp.commands:
            return
        
        self.chkLatestCmd.set_active(False)
        
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.set_log, vc_cmd)
        
    def set_log(self, vc_cmd):
        self.viewLog.set_log(vc_cmd)
    
    # 需要移动到 ViewCmdGroup中
    def move_up_cmd(self):
        selection = self.cmdList.get_selection()
        (model, iter_) = selection.get_selected()
        if iter_ is None:
            return
        
        liststore = self.cmdList.get_model()
        niter = liststore.iter_previous(iter_)
        if niter is not None:
            # 改变内部的数组
            pos = liststore.get_path(iter_).get_indices()[0]
            new_pos = pos - 1 
            
            cmds = self.vc_cmd_grp.commands
            obj = cmds[pos]
            cmds[pos] = cmds[new_pos]
            cmds[new_pos] = obj
            
            # 改变模拟型
            liststore.move_before(iter_, niter)
        
    # 需要移动到 ViewCmdGroup中
    def move_down_cmd(self):
        selection = self.cmdList.get_selection()
        (model, iter_) = selection.get_selected()
        if iter_ is None:
            return
        
        liststore = self.cmdList.get_model()
        niter = liststore.iter_next(iter_)
        if niter is not None:
            # 改变内部的数组
            pos = liststore.get_path(iter_).get_indices()[0]
            new_pos = pos + 1 
            
            cmds = self.vc_cmd_grp.commands
            obj = cmds[pos]
            cmds[pos] = cmds[new_pos]
            cmds[new_pos] = obj
            
            # 改变模拟型
            liststore.move_after(iter_, niter)
            
    # 需要移动到 ViewCmdGroup中
    def add_cmd(self):
        
        liststore = self.cmdList.get_model()
        cmds = self.vc_cmd_grp.commands
        
        cmd = VcCmd("", True)
        
        selection = self.cmdList.get_selection()
        (model, iter_) = selection.get_selected()
        if iter_ is None:
            # 加在最后。
            cmds.append(cmd)
            
            iter_ = liststore.insert(-1)
            self.viewCmdGroup.refresh(iter_, cmd)
            
        else:
            # 有选中项目，新的项目加入到下面
            pos = liststore.get_path(iter_).get_indices()[0]
            cmds.insert(pos+1, cmd)
            
            iter_ = liststore.insert(pos+1)
            self.viewCmdGroup.refresh(iter_, cmd)
    
    # 需要移动到 ViewCmdGroup中
    def del_cmd(self):
        selection = self.cmdList.get_selection()
        (model, iter_) = selection.get_selected()
        if iter_ is None:
            return
        
        liststore = self.cmdList.get_model()
        
        # 改变内部的数组
        pos = liststore.get_path(iter_).get_indices()[0]
        cmds = self.vc_cmd_grp.commands
        cmds.remove(cmds[pos])
        
        # 改变模拟型
        liststore.remove(iter_)
        
class OnePage:
    def __init__(self, info, view):
        self.info = info
        self.view = view

class ViewMultiPages:
    ''' 管理多页
    用PageInfo标志每个页的基本信息
    用PageView管理每个页内的控件
    '''
    
    def __init__(self, on_process_func):
        ''' on_process_func 外部的方法，供调用。 '''
        
        self.on_process_func = on_process_func
        
        # 生成Tab page 类型的控件。
        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.connect("switch_page", self.on_switch_page)
        self.notebook.connect("page-reordered", self.on_page_reordered)
        
        # 包含文件信息和编辑器的信息字典，Key是文件绝对路径
        self.dic_editors = OrderedDict()

    def set_tab_label_by_state(self, label, name, is_modified):
        
        title = name
        if is_modified:
            title = "<span foreground='red'>" + title + " *</span>"
        else:
            title = "<span foreground='black'>" + title + "</span>"
        
        label.set_markup(title)
        
    def get_notebook(self):
        ''' 得到内部的NoteBook控件。'''
        return self.notebook
    
    def get_current_page(self):
        '''
        得到当前的编辑器。
        如果没有打开的编辑器，就返回None
        '''
        index = self.notebook.get_current_page()
        if index < 0 :
            return None
        
        oneEditor = self.dic_editors.values()[index]
        
        return oneEditor.cmdList
    
    def get_current_ide_file(self):
        ''' 得到当前的编辑器编辑的文件。
        return ModelFile 编辑的文件，None：如果不存在 
        '''
        
        index = self.notebook.get_current_page()
        if index < 0 :
            return None
        
        oneEditor = self.dic_editors.values()[index]
        
        return oneEditor.ide_file
    
    def get_editor_by_path(self, abs_file_path):
        index = self._index_of_path(abs_file_path)
        if index < 0 :
            return None
        
        oneEditor = self.dic_editors.values()[index]
        
        return oneEditor
    
    def get_current_ide_editor(self):
        ''' 得到当前的编辑器编辑的文件。
        return ModelFile 编辑的文件，None：如果不存在 
        '''
        
        index = self.notebook.get_current_page()
        if index < 0 :
            return None
        
        oneEditor = self.dic_editors.values()[index]
        
        return oneEditor
    
    def get_current_name(self):
        ''' 获取当前的page的名字。 
        '''
        index = self.notebook.get_current_page()
        if index < 0 :
            return None
        
        name = self.dic_editors.keys()[index]
        return name
    
    def show_command_group(self, name):
        ''' 显示一个文件在编辑器中，
        如果文件已经打开，显示此文件的编辑器放在最前面。
        如果没有打开，就打开。
        '''
        
        if name in self.dic_editors: # 文件已经打开过
            current_name = self.get_current_name()
            if current_name == name:
                # 当前打开的文件正是此文件，就无需再打开。
                return 
            
        else:  # 文件没有打开过。
            # 打开并且读取文件内容到编辑器
            vc_cmd_grp = VcCmdGroupMng.find(name)
            
            vbox, editor = self._create_cmdgroup_tree(vc_cmd_grp)

            tab_label = Gtk.Label()
            self.set_tab_label_by_state(tab_label, name, False)
            index = self.notebook.append_page(vbox, tab_label)
            
            # 允许调整位置.
            self.notebook.set_tab_reorderable(self.notebook.get_nth_page(index), True)
            
            self.dic_editors[name] = OnePage(vc_cmd_grp, editor)

        index = self._index_of_path(name)
        
        self.notebook.set_current_page(index)

    def close_command_group(self, name=None):
        '''
        关闭对应的编辑器
        abs_file_path string 文件的绝对路径（作为唯一的标志）
        return False:关闭失败，比如没有这个文件，或者客户又选择不关闭。
        '''
        
        if name is None:
            # 关闭当前的编辑器
            name = self.get_current_name()
        elif not name in self.dic_editors:
            # 指定的命令组没有打开过，就退出
            return False
        
        onePage = self.dic_editors[name]
        index = self._index_of_path(name)
        
        onePage.view.on_close()
        
        self.notebook.remove_page(index)
        self.dic_editors.pop(name)
        
        # 关闭文件
        #onePage.ide_file.close_file()
        
    def freeze_cmdgroup_tree(self, editor):
        ''' 冻结命令编辑列表 '''
        #completion = cmdList.props.completion
        #completion.block_interactive()
        
    def unfreeze_cmdgroup_tree(self, editor):
        ''' 解冻命令编辑列表 '''
        #completion = cmdList.props.completion
        #completion.unblock_interactive()
        
    def _index_of_path(self, abs_file_path):
        
        index = 0
        for path in self.dic_editors.keys():
            if path == abs_file_path:
                return index
            index += 1
            
        return -1

    def _create_cmdgroup_tree(self, vc_cmd_grp):
        # 生成命令组编辑器
        self.page_view = ViewPage(vc_cmd_grp)
        self.page_view.layout()
        return (self.page_view.panedCmdAndLog, self.page_view)
    
    def on_switch_page(self, notebook, page, page_num):
        ''' 当切换Page时，发生，无论是用户手动还是编程方法调用。
        page Gtk.Widget 切换到的页的控件
        page_num int 切换到的页的索引
        '''
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self._on_switch_page, page_num)
        
    def _on_switch_page(self, page_num):
        abs_file_path = self.dic_editors.keys()[page_num]
        #self.on_process_func(self.notebook, ViewMenu.ACTION_EDITOR_SWITCH_PAGE, abs_file_path)
        
    def on_page_reordered(self, notebook, child_view, page_num):
        # child_view is ScrollView
        old_page_num = 0
        for editor in self.dic_editors.values():
            if editor.cmdList in child_view.get_children():
                break
            old_page_num = old_page_num + 1
        
        # 将OrderedDict转化成数组，进行删除和添加操作。
        items = self.dic_editors.items()
        
        item = items.pop(old_page_num)
        items.insert(page_num, item)
        
        # 然后将变化后的数组再放入到OrderedDict中。
        new_dic = OrderedDict()
        
        for k, v in items:
            new_dic[k] = v
        
        # 将模块的引用修改成新的数据结构。
        self.dic_editors = new_dic
