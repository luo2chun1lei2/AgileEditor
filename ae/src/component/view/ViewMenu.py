# -*- coding:utf-8 -*-

# 菜单和工具的组件。

import logging
from gi.repository import Gtk, Gdk, GtkSource

from framework.FwComponent import FwComponent
from framework.FwManager import FwManager

# 菜单的设定。
MENU_CONFIG = """
<ui>
    <menubar name='MenuBar'>
        <menu action='ProjectMenu'>
        </menu>
        <menu action='FileMenu'>
        </menu>
        <menu action='EditMenu'>
        </menu>
        <menu action='SearchMenu'>
        </menu>
    </menubar>

    <toolbar name='ToolBar'>
    </toolbar>
</ui>
"""

class ViewMenu(FwComponent):
    # 管理菜单和工具栏

    # 当前的状态。
    (
     STATUS_PROJECT_NONE,  # 没有打开的项目
     # STATUS_PROJECT_OPEN, # 打开了文件
     STATUS_FILE_NONE,  # 项目已经打开，没有任何打开的文件
     STATUS_FILE_OPEN,  # 项目已经打开，打开文件，且没有任何的修改。
     STATUS_FILE_OPEN_CHANGED,  # 项目已经打开，文件打开状态，且已经有了修改。
    ) = range(4)

    def __init__(self):
        super(ViewMenu, self).__init__()

        # 附件检索的控件
        self.search_entry = None
        self.actions = []

        self._create_menu()

    # from component
    def onRegistered(self, manager):
        info = [{'name':'view.menu.add', 'help':'add item in menu.'},
                {'name':'view.menu.add_toolbar', 'help':'add item in tool bar.'},
                {'name':'view.menu.get_self', 'help':'get the menu.'},
                {'name':'view.menu.set_accel', 'help':'set accelerator keys.'}
                ]
        manager.register_service(info, self)

        return True

    # from component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "view.menu.add":
            self._add_menu_item(params)
            return (True, None)
        if serviceName == "view.menu.add_toolbar":
            self._add_toolbar_item(params)
            return (True, None)
        elif serviceName == 'view.menu.get_self':
            return (True, {'self': self})
        elif serviceName == 'view.menu.set_accel':
            # 快捷菜单
            window = params['window']
            window.add_accel_group(self.uimanager.get_accel_group())
        else:
            return (False, None)

    def _add_menu_item(self, params):
        ''' 根据设定，加入一个菜单项目
        @param menuName: string: 菜单栏目的名字
        @param menuItemName: string: 菜单项目的名字
        @param title: string: 菜单显示的名字
        @param accel: string: 快捷键
        '''
        menuName = params['menu_name']
        menuItemName = params['menu_item_name']
        title = params['title']
        accel = params['accel']
        stock_id = params['stock_id']
        serviceName = params['service_name']

        # 添加到menu上。
        actionGroups = self.uimanager.get_action_groups()
        actionGroup = actionGroups[0]
        if actionGroup.get_action(menuItemName) is not None:
            logging.debug("There is %s in menu." % menuItemName)
            return

        strMenu = """ <ui> <menubar name='MenuBar'>
                    <menu action='%s'><menuitem action='%s' /></menu>
            </menubar> </ui> """ % (menuName, menuItemName)
        self.uimanager.add_ui_from_string(strMenu)

        action = Gtk.Action(menuItemName, title, title, stock_id)
        action.connect("activate", self.on_menuitem_active_send_service, serviceName)
        if not accel is None:
            actionGroup.add_action_with_accel(action, accel)

        self.actions.append(action)

        # 添加到Toolbar上
        if 'in_toolbar' in params:
            strMenu = """ <toolbar name='ToolBar'>
                        <toolitem action='%s' /></toolbar>""" % (menuItemName)
            self.uimanager.add_ui_from_string(strMenu)

    def _add_toolbar_item(self, params):
        # 添加进度条
        view = params['view']
        if view.get_parent() is not None:
            return
        tool_item = Gtk.ToolItem()
        tool_item.add(view)
        self.toolbar.insert(tool_item, -1)

    def set_status(self, status):
        ''' 目前无法实现此status的切换，所以暂时不再使用
        '''
        if True:
            return
        self.menu_status = status

#         if self.menu_status == self.STATUS_PROJECT_NONE:
#             self.action_project_new.set_sensitive(True)
#             self.action_project_open.set_sensitive(True)
#             self.action_workshop_preferences.set_sensitive(False)
#             self.action_project_close.set_sensitive(False)
#
#             self.action_file_new.set_sensitive(False)
#             self.action_file_open.set_sensitive(False)
#             self.action_file_close.set_sensitive(False)
#             self.action_file_save.set_sensitive(False)
#             self.action_file_save_as.set_sensitive(False)
#
#         elif self.menu_status == self.STATUS_FILE_OPEN:
#
#             self.action_project_new.set_sensitive(True)
#             self.action_project_open.set_sensitive(True)
#             self.action_workshop_preferences.set_sensitive(True)
#             self.action_project_close.set_sensitive(True)
#
#             self.action_file_new.set_sensitive(True)
#             self.action_file_open.set_sensitive(True)
#             self.action_file_close.set_sensitive(True)
#             self.action_file_save.set_sensitive(False)
#             self.action_file_save_as.set_sensitive(True)
#
#         elif self.menu_status == self.STATUS_FILE_OPEN_CHANGED:
#             self.action_project_new.set_sensitive(True)
#             self.action_project_open.set_sensitive(True)
#             self.action_workshop_preferences.set_sensitive(True)
#             self.action_project_close.set_sensitive(True)
#
#             self.action_file_new.set_sensitive(True)
#             self.action_file_open.set_sensitive(True)
#             self.action_file_close.set_sensitive(True)
#             self.action_file_save.set_sensitive(True)
#             self.action_file_save_as.set_sensitive(True)
#
#         else:  # STATUS_FILE_NONE:
#             self.action_project_new.set_sensitive(True)
#             self.action_project_open.set_sensitive(True)
#             self.action_workshop_preferences.set_sensitive(True)
#             self.action_project_close.set_sensitive(True)
#
#             self.action_file_new.set_sensitive(True)
#             self.action_file_open.set_sensitive(True)
#             self.action_file_close.set_sensitive(False)
#             self.action_file_save.set_sensitive(False)
#             self.action_file_save_as.set_sensitive(False)

    def get_status(self):
        return self.menu_status

    def _create_menu(self):
        # 创建菜单和工具栏

        # 主菜单
        action_group = Gtk.ActionGroup("menu_actions")

        self.add_project_menu_actions(action_group)
        self.add_file_menu_actions(action_group)
        self.add_edit_menu_actions(action_group)
        self.add_search_menu_actions(action_group)
        self.add_help_menu_actions(action_group)

        self.uimanager = self.create_ui_manager()
        self.uimanager.insert_action_group(action_group)

        self.menubar = self.uimanager.get_widget("/MenuBar")

        # 工具栏供
        self.toolbar = self.uimanager.get_widget("/ToolBar")

        # 下面的弹出菜单
        # eventbox = Gtk.EventBox()
        # eventbox.connect("button-press-event", self.on_button_press_event)
        # box.pack_start(eventbox, True, True, 0)

        # label = Gtk.Label("Right-click to see the popup menu.")
        # eventbox.add(label)

        # self.popup = uimanager.get_widget("/PopupMenu")

    def add_project_menu_actions(self, action_group):
        # Project菜单设定。
        action_projectmenu = Gtk.Action("ProjectMenu", "Project", None, None)
        action_group.add_action(action_projectmenu)

    def add_file_menu_actions(self, action_group):
        # File项目的菜单设定。
        action_filemenu = Gtk.Action("FileMenu", "File", None, None)
        action_group.add_action(action_filemenu)

    def add_edit_menu_actions(self, action_group):
        action_group.add_actions([
            ("EditMenu", None, "Edit"),
        ])

    def add_search_menu_actions(self, action_group):
        action_group.add_actions([
            ("SearchMenu", None, "Search"),
        ])

    def add_help_menu_actions(self, action_group):
        # Help菜单设定。
        action_helptmenu = Gtk.Action("HelpMenu", "Help", None, None)
        action_group.add_action(action_helptmenu)

    def create_ui_manager(self):

        uimanager = Gtk.UIManager()

        # Throws exception if something went wrong
        uimanager.add_ui_from_string(MENU_CONFIG)

        # Add the accelerator group to the toplevel window
        # accelgroup = uimanager.get_accel_group()
        # self.add_accel_group(accelgroup)

        return uimanager

    def on_menuitem_active_send_service(self, widget, service):
        ''' 通用的菜单 Active 函数，发送service'''
        logging.debug("Common process of one menu item and send service.")
        FwManager.instance().request_service(service, None)

