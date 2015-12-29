#-*- coding:utf-8 -*-

from gi.repository import Gtk, Gdk, GObject, GLib

from VcCmd import *
from __builtin__ import isinstance

class CmdGObject(GObject.GObject):
    
    __gtype_name__ = 'CmdGObject'
    
    def __init__(self, cmd):

        GObject.GObject.__init__(self)
        
        self.cmd = cmd
                 
# 需要注册这个对象到GObject中。
GObject.type_register(CmdGObject)

class ViewCmdGroup:
    ''' 显示和编辑命令组的控件 '''
    
    (COLUMN_IS_SELECTED,
     COLUMN_CMD,
     COLUMN_PARAM,
     COLUMN_PROGRESS,
     COLUMN_IS_OK,
     COLUMN_CMD_OBJ,
     COLUMN_CMD_START_PROCESS,
     NUM_COLUMNS) = range(8)
    
    def __init__(self, vc_cmd_grp):
        
        # 滚动条
        scrolledCtrl = Gtk.ScrolledWindow()
        scrolledCtrl.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scrolledCtrl.set_hexpand(True)
        scrolledCtrl.set_vexpand(True)
        
        self.scrolledCtrl = scrolledCtrl
        
        # 生成模型
        self.vc_cmd_grp = vc_cmd_grp
        self.model = self.create_model(self.vc_cmd_grp)
        
        # 命令组的编辑器
        treeview = Gtk.TreeView(model=self.model)
        treeview.set_rules_hint(True)
        
        self.add_columns(treeview)
        treeview.connect("row-activated", self.on_row_activated, self.model)
        
        self.treeview = treeview
        
        scrolledCtrl.add(treeview)
        
        VcEventPipe.register_event(VcEventPipe.EVENT_CMD_START, self.sm_on_cmd_start)
        VcEventPipe.register_event(VcEventPipe.EVENT_CMD_PROCESS, self.sm_on_cmd_process)
        VcEventPipe.register_event(VcEventPipe.EVENT_CMD_FINISH, self.sm_on_cmd_finish)
        VcEventPipe.register_event(VcEventPipe.EVENT_CMD_GRP_CANCEL, self.sm_on_cmd_grp_cancel)
        VcEventPipe.register_event(VcEventPipe.EVENT_CMD_GRP_FINISH, self.sm_on_cmd_grp_finish)
        
        # 可以编辑
        self.unfreeze()
        
    def unregister(self):
        VcEventPipe.unregister_event(VcEventPipe.EVENT_CMD_START, self.sm_on_cmd_start)
        VcEventPipe.unregister_event(VcEventPipe.EVENT_CMD_PROCESS, self.sm_on_cmd_process)
        VcEventPipe.unregister_event(VcEventPipe.EVENT_CMD_FINISH, self.sm_on_cmd_finish)
        VcEventPipe.unregister_event(VcEventPipe.EVENT_CMD_GRP_CANCEL, self.sm_on_cmd_grp_cancel)
        VcEventPipe.unregister_event(VcEventPipe.EVENT_CMD_GRP_FINISH, self.sm_on_cmd_grp_finish)
        

    def create_model(self, vc_cmd_grp):
        model = Gtk.ListStore(bool,
                                   str,
                                   str,
                                   GObject.TYPE_INT,    # 进度条
                                   str,
                                   GObject.TYPE_OBJECT,
                                   bool)

        self.data = vc_cmd_grp.commands
        for cmd in self.data:
            iter_ = model.insert(-1)
            self._set_cmd(model, iter_, cmd)
            
        return model
    
    def _set_cmd(self, model, iter_, cmd):
        # 根据命令当前的进度得到运行的情况。
        if cmd.process == 0:
            # 还没有运行
            process = 0
            start_process = False
            icon_name = ""
        elif cmd.process < 100:
            # 正在运行
            process = cmd.process
            start_process = True
            icon_name = ""
        elif cmd.process == 100:
            # 运行完成（成功）
            process = 0
            start_process = False
            icon_name = Gtk.STOCK_OK
        else: # < 0
            # 运行失败
            process = 0
            start_process = False
            icon_name = Gtk.STOCK_NO

        model.set(iter_, [0, 1, 2, 3, 4, 5, 6], 
                  [cmd.is_selected,
                           cmd.get_content(),
                           cmd.get_param(),
                           process,
                           icon_name,
                           CmdGObject(cmd),
                           start_process])

    def create_selected_cmd_list(self):
        ''' 生成可以选择的命令列表。'''
        self.cmds = Gtk.ListStore(str)
        for cmd in VcCmdTemplateMng.instance().list:
            self.cmds.append([cmd.get_content()])
            
        return self.cmds
    
    def freeze(self):
        ''' 禁止编辑 '''
        self.renderer_is_selected.set_property("activatable", False)
        self.renderer_content.set_property("editable", False)
        self.renderer_name.set_property("editable", False)
        
    def unfreeze(self):
        ''' 允许编辑 '''
        self.renderer_is_selected.set_property("activatable", True)
        self.renderer_content.set_property("editable", True)
        self.renderer_name.set_property("editable", True)
        
        #TODO:无法马上更新。
        
    def refresh(self, iter_, vc_cmd):
        # 根据当前最新的数据，更新画面的显示。
        self._set_cmd(self.model, iter_, vc_cmd)
    
    def add_columns(self, treeview):
        
        model = treeview.get_model()

        # 是否需要执行
        renderer = Gtk.CellRendererToggle()
        renderer.connect('toggled', self.on_is_selected_toggled, model)
        self.renderer_is_selected = renderer
        
        column = Gtk.TreeViewColumn("选中", renderer, active=self.COLUMN_IS_SELECTED)
        column.set_fixed_width(50)
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column.set_alignment(0.5)
        treeview.append_column(column)

        # 命令类型
        renderer = Gtk.CellRendererCombo()
        renderer.set_property("text-column", 0)
        renderer.set_property("model", self.create_selected_cmd_list())
        renderer.connect("changed",self.on_cmd_content_changed, model);
        self.renderer_content = renderer
        
        column = Gtk.TreeViewColumn("命令", renderer, text=self.COLUMN_CMD)
        #column.set_sort_column_id(self.COLUMN_SEVERITY)
        #column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column.set_resizable(True)
        column.set_expand(True)
        column.set_alignment(0.5)
        
        treeview.append_column(column)

        # 命令内容或者参数
        renderer = Gtk.CellRendererText()
        renderer.connect("edited",self.on_param_edited, model);
        self.renderer_name = renderer
        
        column = Gtk.TreeViewColumn("详细", renderer, text=self.COLUMN_PARAM)
        #column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column.set_alignment(0.5)
        column.set_expand(True)
        column.set_resizable(True)
        
        treeview.append_column(column)

        # 是否正在运行
        renderer = Gtk.CellRendererSpinner()
        
        column = Gtk.TreeViewColumn("运行", renderer, pulse=self.COLUMN_PROGRESS,
                                    active=self.COLUMN_CMD_START_PROCESS)
        column.set_min_width(50)
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column.set_alignment(0.5)
        
        treeview.append_column(column)

        # 是否成功
        renderer = Gtk.CellRendererPixbuf()
        renderer.props.follow_state = True
        
        column = Gtk.TreeViewColumn("结果", renderer, stock_id = self.COLUMN_IS_OK)
                                    #sensitive=self.COLUMN_SENSITIVE)
        #column.set_sort_column_id(self.COLUMN_ICON)
        column.set_min_width(50)
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        
        column.set_expand(False)
        column.set_alignment(0.5)
        
        treeview.append_column(column)
        
    def on_is_selected_toggled(self, cell, path_str, model):
        ''' 当改变命令是否被选中时。'''
        
        # get toggled iter
        iter_ = model.get_iter(path_str)
        vc_cmd = model.get_value(iter_, self.COLUMN_CMD_OBJ).cmd
 
        # 当前值取反
        vc_cmd.is_selected = not vc_cmd.is_selected
 
        model.set_value(iter_, self.COLUMN_IS_SELECTED, vc_cmd.is_selected)
        
    def on_cmd_content_changed(self, cell, path_str, new_iter, model):
        
        iter_ = model.get_iter(path_str)
        vc_cmd = model.get_value(iter_, self.COLUMN_CMD_OBJ).cmd
        
        list_model = self.cmds
        content = list_model.get_value(new_iter, 0)
        
        vc_cmd.set_content(content)
        
        #TODO:有异常显示。
        model.set_value(iter_, self.COLUMN_CMD, vc_cmd.get_content())

    def on_param_edited(self, cell, path_str, new_text, model):
        iter_ = model.get_iter(path_str)
        vc_cmd = model.get_value(iter_, self.COLUMN_CMD_OBJ).cmd
        
        vc_cmd.set_param(new_text)
        
        model.set_value(iter_, self.COLUMN_PARAM, vc_cmd.get_param())
        
    def on_row_activated(self, treeview, path_str, column, model):
        iter_ = model.get_iter(path_str)
        vc_cmd = model.get_value(iter_, self.COLUMN_CMD_OBJ).cmd
        
        VcEventPipe.send_event(VcEventPipe.EVENT_LOG_SET, vc_cmd)
        
    def sm_on_cmd_start(self, vc_cmd):
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self._on_cmd_start, vc_cmd)
        
    def _on_cmd_start(self, vc_cmd):
        
        # 如果命令不是这个命令组中的，就退出
        if vc_cmd not in self.vc_cmd_grp.commands:
            return
        
        index = self.vc_cmd_grp.commands.index(vc_cmd)
        if index < 0:
            return
        
        vc_cmd.process = 0
        
        model = self.treeview.get_model()
        iter_ = model.get_iter(Gtk.TreePath.new_from_string( str(index) ))
        model.set_value(iter_, self.COLUMN_PROGRESS, vc_cmd.process)
        model.set_value(iter_, self.COLUMN_CMD_START_PROCESS, True)
        
        # 新命令开始执行。
        VcEventPipe.send_event(VcEventPipe.EVENT_LOG_COMMAND_START, vc_cmd)
        
    def sm_on_cmd_process(self, vc_cmd, process):
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self._on_cmd_process, vc_cmd, process)
        
    def _on_cmd_process(self, vc_cmd, process):
        
        # 如果命令不是这个命令组中的，就退出
        if vc_cmd not in self.vc_cmd_grp.commands:
            return
        
        index = self.vc_cmd_grp.commands.index(vc_cmd)
        if index < 0:
            return
        
        vc_cmd.process = process
        
        model = self.treeview.get_model()
        iter_ = model.get_iter(Gtk.TreePath.new_from_string( str(index) ))
        model.set_value(iter_, self.COLUMN_PROGRESS, vc_cmd.process)
    
    def sm_on_cmd_finish(self, vc_cmd, is_ok, result):
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self._on_cmd_finish, vc_cmd, is_ok, result)
        
    def _on_cmd_finish(self, vc_cmd, is_ok, result):
        
        # 如果命令不是这个命令组中的，就退出
        if vc_cmd not in self.vc_cmd_grp.commands:
            return
        
        index = self.vc_cmd_grp.commands.index(vc_cmd)
        if index < 0:
            return
        
        vc_cmd.process = 0
        if is_ok:
            icon_name = Gtk.STOCK_OK
        else:
            icon_name = Gtk.STOCK_NO
        
        model = self.treeview.get_model()
        iter_ = model.get_iter(Gtk.TreePath.new_from_string( str(index) ))
        
        model.set_value(iter_, self.COLUMN_PROGRESS, vc_cmd.process)
        model.set_value(iter_, self.COLUMN_CMD_START_PROCESS, False)
        model.set_value(iter_, self.COLUMN_IS_OK, icon_name)
        
#         if index == len(self.vc_cmd_grp.commands) - 1:
#             # 是最后一个
#             self.unfreeze()
        
    def sm_on_cmd_grp_cancel(self, vc_cmd_grp):
        
        if vc_cmd_grp is not self.vc_cmd_grp:
            return
        
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self._on_cmd_cancel)
        
    def _on_cmd_cancel(self):
        self.unfreeze()
        
    def sm_on_cmd_grp_finish(self, vc_cmd_grp):
        
        if vc_cmd_grp is not self.vc_cmd_grp:
            return
        
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self._on_cmd_grp_finish)
        
    def _on_cmd_grp_finish(self):
        self.unfreeze()
