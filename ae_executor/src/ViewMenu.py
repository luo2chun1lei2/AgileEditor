#-*- coding:utf-8 -*-

'''
菜单和工具的模块。
'''

from gi.repository import Gtk, Gdk, GtkSource

# 菜单的设定。
MENU_CONFIG = """
<ui>
    <menubar name='MenuBar'>
        <menu action='MenuApp'>
            <menuitem action='ItemApply' />
            <menuitem action='ItemDiscard' />
        </menu>
        <menu action='MenuEdit'>
            <menuitem action='ItemExecute' />
            <menuitem action='ItemKeep' />
            <menuitem action='ItemUndo' />
            <menuitem action='ItemRestore' />
        </menu>
        <menu action='HelpMenu'>
            <menuitem action='HelpInfo' />
        </menu>
    </menubar>

    <toolbar name='ToolBar'>
        <toolitem action='ItemApply' />
        <toolitem action='ItemDiscard' />
        <separator />
        <toolitem action='ItemExecute' />
        <toolitem action='ItemKeep' />
        <toolitem action='ItemUndo' />
        <toolitem action='ItemRestore' />
    </toolbar>
</ui>
"""

class ViewMenu(object):
    '''
    管理菜单和工具栏
    '''

    # 可以发出的命令。 
    (
     ACTION_APPLY,
     ACTION_DISCARD,
     
     ACTION_EXECUTE,
     ACTION_BACK_TO,
     ACTION_KEEP,
     ACTION_UNDO,
     ACTION_RESTORE,
     
     ACTION_HELP_INFO
     ) = range(8)

    def __init__(self, window, on_process_func):
        
        self.on_process_func = on_process_func
        
        self._create_menu(window)

    def _create_menu(self, window):
        ''' 创建菜单 '''
        # 菜单
        action_group = Gtk.ActionGroup("menu_actions")
        
        self.add_app_menu_actions(action_group)
        self.add_edit_menu_actions(action_group)
        self.add_help_menu_actions(action_group)

        uimanager = self.create_ui_manager()
        uimanager.insert_action_group(action_group)

        menubar = uimanager.get_widget("/MenuBar")
        
        self.menubar = menubar
        
        # 工具栏供
        toolbar = uimanager.get_widget("/ToolBar")
        self.toolbar = toolbar
        
        # 快捷菜单
        window.add_accel_group(uimanager.get_accel_group())
        
    def add_app_menu_actions(self, action_group):
        ''' App菜单设定。 '''
        # 快捷键请参考 gdkkeysyms.h中的GDK_KEY_xxxx。
        action_app_menu = Gtk.Action("MenuApp", "App", None, None)
        action_group.add_action(action_app_menu)

        action_apply = Gtk.Action("ItemApply", None, None, Gtk.STOCK_APPLY)
        action_apply.connect("activate", self.on_menu_action_apply)
        action_group.add_action_with_accel(action_apply, "<Control>Escape")
        self.action_group = action_apply
        
        action_discard = Gtk.Action("ItemDiscard", None, None, Gtk.STOCK_CANCEL)
        action_discard.connect("activate", self.on_menu_action_discard)
        action_group.add_action_with_accel(action_discard, "<control>q") #apostrophe
        self.action_discard = action_discard
        
    def add_edit_menu_actions(self, action_group):
        ''' Command项目的菜单设定。 '''
        action_command_menu = Gtk.Action("MenuEdit", "Edit", None, None)
        action_group.add_action(action_command_menu)

        action_edit_execute = Gtk.Action("ItemExecute", None, None, Gtk.STOCK_EXECUTE)
        action_edit_execute.connect("activate", self.on_menu_edit_execute)
        action_group.add_action_with_accel(action_edit_execute, "<control>Return")
        self.action_edit_execute = action_edit_execute
        
        action_edit_keep = Gtk.Action("ItemKeep", "Keep", None, Gtk.STOCK_SAVE)
        action_edit_keep.connect("activate", self.on_menu_edit_keep)
        action_group.add_action_with_accel(action_edit_keep, "<control>k")
        self.action_edit_keep = action_edit_keep
        
        action_edit_undo = Gtk.Action("ItemUndo", None, None, Gtk.STOCK_UNDO)
        action_edit_undo.connect("activate", self.on_menu_edit_undo)
        action_group.add_action_with_accel(action_edit_undo, "<control>Left")
        self.action_edit_undo = action_edit_undo
        
        action_edit_restore = Gtk.Action("ItemRestore", "Restore", None, Gtk.STOCK_GOTO_FIRST)
        action_edit_restore.connect("activate", self.on_menu_edit_restore)
        action_group.add_action_with_accel(action_edit_restore, "<control>Home")
        self.action_edit_store = action_edit_restore

    def add_help_menu_actions(self, action_group):
        ''' Help菜单设定。 '''
        action_helptmenu = Gtk.Action("HelpMenu", "Help", None, None)
        action_group.add_action(action_helptmenu)

        action_help_info = Gtk.Action("HelpInfo", None, "Information", Gtk.STOCK_INFO)
        action_help_info.connect("activate", self.on_menu_help_info)
        action_group.add_action_with_accel(action_help_info, "<control>H")
        self.action_help_info = action_help_info
        
    def create_ui_manager(self):
        
        uimanager = Gtk.UIManager()
        uimanager.add_ui_from_string(MENU_CONFIG)
    
        return uimanager
    
    def on_menu_action_apply(self, widget):
        print("A App|Apply as menu item was selected.")
        self.on_process_func(widget, self.ACTION_APPLY)
        
    def on_menu_action_discard(self, widget):
        print("A App|Discard And Quit as menu item was selected.")
        self.on_process_func(widget, self.ACTION_DISCARD)
    
    def on_menu_edit_execute(self, widget):
        print("A Edit|Execute menu item was selected.")
        self.on_process_func(widget, self.ACTION_EXECUTE)
        
    def on_menu_edit_keep(self, widget):
        print('A Edit|Keep menu item was selected.')
        self.on_process_func(widget, self.ACTION_KEEP)
    
    def on_menu_edit_undo(self, widget):
        print("A Edit|Undo menu item was selected.")
        self.on_process_func(widget, self.ACTION_UNDO)
        
    def on_menu_edit_restore(self, widget):
        print("A Edit|Restore menu item was selected.")
        self.on_process_func(widget, self.ACTION_RESTORE)
    
    def on_menu_help_info(self, widget):
        print("A Help|Infomation as menu item was selected.")
        self.on_process_func(widget, self.ACTION_HELP_INFO)
