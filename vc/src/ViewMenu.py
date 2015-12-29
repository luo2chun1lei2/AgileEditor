#-*- coding:utf-8 -*-

'''
菜单和工具的模块。
'''

from gi.repository import Gtk, Gdk, GtkSource

# 菜单的设定。
MENU_CONFIG = """
<ui>
    <menubar name='MenuBar'>
        <menu action='AppMenu'>
            <menuitem action='AppQuit' />
        </menu>
        <menu action='CommandGroupMenu'>
            <menuitem action='CommandGroupNew' />
            <menuitem action='CommandGroupOpen' />
            <menuitem action='CommandGroupClose' />
            <menuitem action='CommandGroupDelete' />
            <menuitem action='CommandGroupSave' />
        </menu>
        <menu action='CommandMenu'>
            <menuitem action='CommandAdd' />
            <menuitem action='CommandDelete' />
            <menuitem action='CommandModify' />
            <menuitem action='CommandUp' />
            <menuitem action='CommandDown' />
        </menu>
        <menu action='HelpMenu'>
            <menuitem action='HelpInfo' />
        </menu>
    </menubar>

    <toolbar name='ToolBar'>
        <toolitem action='CommandGroupNew' />
        <toolitem action='CommandGroupOpen' />
        <toolitem action='CommandGroupClose' />
        <toolitem action='CommandGroupDelete' />
        <toolitem action='CommandGroupSave' />
    </toolbar>
</ui>
"""

class ViewMenu(object):
    '''
    管理菜单和工具栏
    '''

    # 可以发出的命令。 
    (
     ACTION_APP_QUIT,
     
     ACTION_COMMAND_ADD,    # 向命令组中添加一个命令
     ACTION_COMMAND_DELETE, # 删除一个命令
     ACTION_COMMAND_MODIFY, # 想修改一个命令
     ACTION_COMMAND_UP,     # 将命令在命令组中的位置提高一个
     ACTION_COMMAND_DOWN,   # 将命令在命令组中的位置降低一个
     
     ACTION_COMMAND_GROUP_NEW,
     ACTION_COMMAND_GROUP_OPEN,
     ACTION_COMMAND_GROUP_CLOSE,
     ACTION_COMMAND_GROUP_SAVE,
     ACTION_COMMAND_GROUP_DELETE,
     
     ACTION_HELP_INFO
     ) = range(12)

    def __init__(self, window, on_menu_func):
        
        self.on_menu_func = on_menu_func
        
        self._create_menu(window)

    def _create_menu(self, window):
        ''' 创建菜单 '''
        # 菜单
        action_group = Gtk.ActionGroup("menu_actions")
        
        self.add_app_menu_actions(action_group)
        self.add_command_menu_actions(action_group)
        self.add_command_group_menu_actions(action_group)
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
        action_app_menu = Gtk.Action("AppMenu", "App", None, None)
        action_group.add_action(action_app_menu)

        action_app_quit = Gtk.Action("AppQuit", None, None, Gtk.STOCK_QUIT)
        action_app_quit.connect("activate", self.on_menu_app_quit)
        action_group.add_action(action_app_quit)
        self.action_app_quit = action_app_quit
    
    def add_command_menu_actions(self, action_group):
        ''' Command项目的菜单设定。 '''
        action_command_menu = Gtk.Action("CommandMenu", "Command", None, None)
        action_group.add_action(action_command_menu)

        action_command_add = Gtk.Action("CommandAdd", None, "Add a command", Gtk.STOCK_ADD)
        action_command_add.connect("activate", self.on_menu_command_add)
        action_group.add_action_with_accel(action_command_add, "<control>equal")
        #action_group.add_action(action_command_add)
        self.action_command_add = action_command_add
        
        action_command_delete = Gtk.Action("CommandDelete", None, "Delete the command", Gtk.STOCK_DELETE)
        action_command_delete.connect("activate", self.on_menu_command_delete)
        action_group.add_action_with_accel(action_command_delete, "<control>D")
        self.action_command_delete = action_command_delete
        
        action_command_modify = Gtk.Action("CommandModify", None, "Modify the command", Gtk.STOCK_EDIT)
        action_command_modify.connect("activate", self.on_menu_command_modify)
        action_group.add_action_with_accel(action_command_modify, "<control>M")
        self.action_command_modify = action_command_modify
        
        action_command_up = Gtk.Action("CommandUp", None, "Move up the command", Gtk.STOCK_GO_UP)
        action_command_up.connect("activate", self.on_menu_command_up)
        action_group.add_action_with_accel(action_command_up, "<control>Up")
        self.action_command_up = action_command_up
        
        action_command_down = Gtk.Action("CommandDown", None, "Move down the command", Gtk.STOCK_GO_DOWN)
        action_command_down.connect("activate", self.on_menu_command_down)
        action_group.add_action_with_accel(action_command_down, "<control>Down")
        self.action_command_down = action_command_down
    
    def add_command_group_menu_actions(self, action_group):
        ''' Command Group项目的菜单设定。 '''
        action_command_menu = Gtk.Action("CommandGroupMenu", "CommandGroup", None, None)
        action_group.add_action(action_command_menu)

        action_command_group_new = Gtk.Action("CommandGroupNew", None, "Create a command group", Gtk.STOCK_NEW)
        action_command_group_new.connect("activate", self.on_menu_command_group_new)
        action_group.add_action_with_accel(action_command_group_new, "<control>N")
        self.action_command_group_new = action_command_group_new
        
        action_command_group_open = Gtk.Action("CommandGroupOpen", None, "Open a command group", Gtk.STOCK_OPEN)
        action_command_group_open.connect("activate", self.on_menu_command_group_open)
        action_group.add_action_with_accel(action_command_group_open, "<control>O")
        self.action_command_group_open = action_command_group_open
        
        action_command_group_close = Gtk.Action("CommandGroupClose", None, "Close current command group", Gtk.STOCK_CLOSE)
        action_command_group_close.connect("activate", self.on_menu_command_group_close)
        action_group.add_action_with_accel(action_command_group_close, "<control>W")
        self.action_command_group_close = action_command_group_close
        
        action_command_group_save = Gtk.Action("CommandGroupSave", None, "Save current command group", Gtk.STOCK_SAVE)
        action_command_group_save.connect("activate", self.on_menu_command_group_save)
        action_group.add_action_with_accel(action_command_group_save, "<control>S")
        self.action_command_group_save = action_command_group_save
        
        action_command_group_delete = Gtk.Action("CommandGroupDelete", None, "Delete current command group", Gtk.STOCK_DELETE)
        action_command_group_delete.connect("activate", self.on_menu_command_group_delete)
        action_group.add_action(action_command_group_delete)
        self.action_command_group_delete = action_command_group_delete

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
    
    def on_menu_app_quit(self, widget):
        print("A App|Quit as menu item was selected.")
        self.on_menu_func(widget, self.ACTION_APP_QUIT)
        
    def on_menu_command_add(self, widget):
        print("A Command|Add menu item was selected.")
        self.on_menu_func(widget, self.ACTION_COMMAND_ADD)
        
    def on_menu_command_delete(self, widget):
        print('A Command|Delete menu item was selected.')
        self.on_menu_func(widget, self.ACTION_COMMAND_DELETE)
    
    def on_menu_command_modify(self, widget):
        print("A Command|Modify menu item was selected.")
        self.on_menu_func(widget, self.ACTION_COMMAND_MODIFY)
        
    def on_menu_command_up(self, widget):
        print("A Command|Up menu item was selected.")
        self.on_menu_func(widget, self.ACTION_COMMAND_UP)
        
    def on_menu_command_down(self, widget):
        print("A Command|Down as menu item was selected.")
        self.on_menu_func(widget, self.ACTION_COMMAND_DOWN)
    
    def on_menu_command_group_new(self, widget):
        print("A CommandGroup|New menu item was selected.")
        self.on_menu_func(widget, self.ACTION_COMMAND_GROUP_NEW)
        
    def on_menu_command_group_open(self, widget):
        print('A CommandGroup|Open menu item was selected.')
        self.on_menu_func(widget, self.ACTION_COMMAND_GROUP_OPEN)
    
    def on_menu_command_group_close(self, widget):
        print("A CommandGroup|Close menu item was selected.")
        self.on_menu_func(widget, self.ACTION_COMMAND_GROUP_CLOSE)
        
    def on_menu_command_group_save(self, widget):
        print("A CommandGroup|Save menu item was selected.")
        self.on_menu_func(widget, self.ACTION_COMMAND_GROUP_SAVE)
        
    def on_menu_command_group_delete(self, widget):
        print("A CommandGroup|Delete as menu item was selected.")
        self.on_menu_func(widget, self.ACTION_COMMAND_GROUP_DELETE)

    def on_menu_help_info(self, widget):
        print("A Help|Information as menu item was selected.")
        self.on_menu_func(widget, self.ACTION_HELP_INFO)
        