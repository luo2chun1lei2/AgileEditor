#-*- coding:utf-8 -*-

'''
显示运行的列表。
'''

from gi.repository import Gtk, Gdk, GObject, GLib, Pango

from VxEventPipe import *
from VxSourceCmd import VxSourceCmdMng
from ViewMenu import ViewMenu

class CmdGObject(GObject.GObject):
    
    __gtype_name__ = 'CmdGObject'
    
    def __init__(self, cmd):

        GObject.GObject.__init__(self)
        
        self.cmd = cmd
                 
# 需要注册这个对象到GObject中。
GObject.type_register(CmdGObject)

class ViewHistoryTextCmd:
    
    '''
    显示和编辑命令组的管理控件 
    '''
    
    (COLUMN_SOURCE,
     COLUMN_COMMAND,
     COLUMN_CMD_OBJ,
     NUM_COLUMNS) = range(4)
    
    def __init__(self, on_process_func):
        
        self.process_func = on_process_func
        
        # 生成模型
        self.model = self.create_model()
         
        # 创建TreeView的控件
        treeview = Gtk.TreeView(model=self.model)
        treeview.set_rules_hint(True)
         
        self.add_columns(treeview)
        treeview.connect("row-activated", self.on_row_activated, self.model)
         
        self.treeview = treeview
         
#         VxEventPipe.register_event(VxEventPipe.EVENT_CMD_START, self.sm_on_cmd_start)
#         VxEventPipe.register_event(VxEventPipe.EVENT_CMD_PROCESS, self.sm_on_cmd_process)
#         VxEventPipe.register_event(VxEventPipe.EVENT_CMD_FINISH, self.sm_on_cmd_finish)
#         VxEventPipe.register_event(VxEventPipe.EVENT_CMD_CANCEL, self.sm_on_cmd_cancel)
        
        # 滚动条。
        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.scrolledwindow.set_size_request(150, 0)
        
        self.scrolledwindow.add(self.treeview)
        
    def create_model(self):
        model = Gtk.ListStore( str, str, GObject.TYPE_OBJECT)

        col = 0
        
        vx_source_cmd_mng = VxSourceCmdMng.instance()
        
        for source_cmd in vx_source_cmd_mng.list:
            model.append([source_cmd.source[0:100],
                               source_cmd.command,
                               CmdGObject(source_cmd)])
            col += 1
        return model
    
    def refresh_model(self):
        model = self.treeview.get_model()
        
        vx_source_cmd_mng = VxSourceCmdMng.instance()
        
        model.clear()
        for source_cmd in vx_source_cmd_mng.list:
            model.append([source_cmd.source[0:100],
                               source_cmd.command,
                               CmdGObject(source_cmd)])

    def create_selected_cmd_list(self):
        ''' 生成可以选择的命令列表。'''
        self.cmds = Gtk.ListStore(str)
        for cmd in VcCmdTemplateMng.instance().list:
            self.cmds.append([cmd.get_content()])
            
        return self.cmds
    
    def add_columns(self, treeview):
        
        # 处理的内容
        renderer = Gtk.CellRendererText()
        renderer.set_property("ellipsize-set", True)
        renderer.set_property("ellipsize", Pango.EllipsizeMode.END)
        renderer.set_fixed_height_from_font(3)
        self.renderer_source = renderer
        
        column = Gtk.TreeViewColumn("文本", renderer, text=self.COLUMN_SOURCE)
        column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column.set_alignment(0)
        column.set_expand(True)
        column.set_resizable(True)
        
        treeview.append_column(column)
        
        # 命令
        renderer = Gtk.CellRendererText()
        self.renderer_command = renderer
        
        column = Gtk.TreeViewColumn("命令", renderer, text=self.COLUMN_COMMAND)
        column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column.set_alignment(0)
        column.set_expand(True)
        column.set_resizable(True)
        
        treeview.append_column(column)
        
    def on_row_activated(self, treeview, path_str, column, model):
        iter_ = model.get_iter(path_str)
        vc_source_cmd = model.get_value(iter_, self.COLUMN_CMD_OBJ).cmd
        
        self.process_func(self, ViewMenu.ACTION_BACK_TO, vc_source_cmd)
        
    def sm_on_cmd_start(self, vc_cmd):
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self._on_cmd_start, vc_cmd)
        
    def _on_cmd_start(self, vc_cmd):
        index = self.vc_cmd_grp.commands.index(vc_cmd)
        if index < 0:
            return
        
        vc_cmd.process = 0
        
        model = self.treeview.get_model()
        iter_ = model.get_iter(Gtk.TreePath.new_from_string( str(index) ))
        model.set_value(iter_, self.COLUMN_PROGRESS, vc_cmd.process)
        model.set_value(iter_, self.COLUMN_CMD_START_PROCESS, True)
        
        # 清除日志输出
        VxEventPipe.send_event(VxEventPipe.EVENT_LOG_CLEAN)
        
    def sm_on_cmd_process(self, vc_cmd, process):
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self._on_cmd_process, vc_cmd, process)
        
    def _on_cmd_process(self, vc_cmd, process):
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
        
        if index == len(self.vc_cmd_grp.commands) - 1:
            # 是最后一个
            self.unfreeze()
        
    def sm_on_cmd_cancel(self):
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self._on_cmd_cancel)
        
    def _on_cmd_cancel(self):
        self.unfreeze()
