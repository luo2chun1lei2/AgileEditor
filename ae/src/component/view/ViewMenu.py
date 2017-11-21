# -*- coding:utf-8 -*-

# 菜单和工具的组件。

import logging
from gi.repository import Gtk, Gdk, GtkSource

from framework.FwComponent import FwComponent
from framework.FwManager import FwManager

class NeedJump:
    def __init__(self, need):
        self.need = need

# 菜单的设定。
MENU_CONFIG = """
<ui>
    <menubar name='MenuBar'>
        <menu action='ProjectMenu'>
            <menuitem action='WorkshopPreferences' />
            <separator />
            <menuitem action='ProjectNew' />
            <menuitem action='ProjectOpen' />
            <menuitem action='ProjectClose' />
            <separator />
            <menuitem action='AppQuit' />
        </menu>
        <menu action='FileMenu'>
            <menuitem action='FileNew' />
            <menuitem action='FileOpen' />
            <menuitem action='FileClose' />
            <separator />
            <menuitem action='FileSave' />
            <menuitem action='FileSaveAs' />
        </menu>
        <menu action='EditMenu'>
        </menu>
        <menu action='SearchMenu'>
        </menu>
    </menubar>

    <toolbar name='ToolBar'>
        <toolitem action='AppQuit' />
        <separator/>
        <toolitem action='FileNew' />
        <toolitem action='FileOpen' />
        <toolitem action='FileSave' />
        <toolitem action='FileClose' />
        <separator/>
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

    # 可以发出的命令。
    (
     ACTION_PROJECT_NEW,
     ACTION_PROJECT_OPEN,
     ACTION_PROJECT_PREFERENCES,
     ACTION_PROJECT_CLOSE,
     ACTION_APP_QUIT,

     ACTION_FILE_NEW,
     ACTION_FILE_OPEN,
     ACTION_FILE_CLOSE,
     ACTION_FILE_SAVE,
     ACTION_FILE_SAVE_AS,

     # 其他地方的功能
     ACTION_EDITOR_SWITCH_PAGE,  # 切换当前编辑的文件
     ) = range(11)

    def __init__(self, window, on_menu_func):

        # 附件检索的控件
        self.search_entry = None
        self.actions = []

        self.on_menu_func = on_menu_func

        self._create_menu(window)

    # from component
    def onRegistered(self, manager):
        info = [{'name':'view.menu.add', 'help':'add item in menu.'},
                {'name':'view.menu.set_and_jump_to_search_textbox', 'help':'jump to search textbox and set text.'}
                ]
        manager.registerService(info, self)

        return True

    # from component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "view.menu.add":
            self._add_menu_item(params)
            return (True, None)
        elif serviceName == "view.menu.set_and_jump_to_search_textbox":
            self._jump_to_search_textbox_and_set_text(params['text'])
            return (True, None)
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
        title =params['title']
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

        action = Gtk.Action(menuItemName, title, None, stock_id)
        if serviceName == 'ctrl.search.find_prev' or serviceName == 'ctrl.search.find_next':
            # TODO 这是两个特例，破坏了菜单实现的一致性，需要仔细研究怎么处理！
            action.connect("activate", self.on_menuitem_active_with_search_text, serviceName)
        else:
            action.connect("activate", self.on_menuitem_active_send_service, serviceName)
        if not accel is None:
            actionGroup.add_action_with_accel(action, accel)

        self.actions.append(action)
        
        # 添加到Toolbar上
        if 'in_toolbar' in params:
            #tool_item = Gtk.ToolItem()
            #self.toolbar.insert(tool_item, -1)
            strMenu = """ <toolbar name='ToolBar'>
                        <toolitem action='%s' /></toolbar>""" % (menuItemName)
        self.uimanager.add_ui_from_string(strMenu)

    def on_stub_menu_func(self, widget, action, param=None, param2=None, param3=None):
        pass

    def set_status(self, status):
        self.menu_status = status

        if self.menu_status == self.STATUS_PROJECT_NONE:
            self.action_project_new.set_sensitive(True)
            self.action_project_open.set_sensitive(True)
            self.action_workshop_preferences.set_sensitive(False)
            self.action_project_close.set_sensitive(False)

            self.action_file_new.set_sensitive(False)
            self.action_file_open.set_sensitive(False)
            self.action_file_close.set_sensitive(False)
            self.action_file_save.set_sensitive(False)
            self.action_file_save_as.set_sensitive(False)

        elif self.menu_status == self.STATUS_FILE_OPEN:

            self.action_project_new.set_sensitive(True)
            self.action_project_open.set_sensitive(True)
            self.action_workshop_preferences.set_sensitive(True)
            self.action_project_close.set_sensitive(True)

            self.action_file_new.set_sensitive(True)
            self.action_file_open.set_sensitive(True)
            self.action_file_close.set_sensitive(True)
            self.action_file_save.set_sensitive(False)
            self.action_file_save_as.set_sensitive(True)

        elif self.menu_status == self.STATUS_FILE_OPEN_CHANGED:
            self.action_project_new.set_sensitive(True)
            self.action_project_open.set_sensitive(True)
            self.action_workshop_preferences.set_sensitive(True)
            self.action_project_close.set_sensitive(True)

            self.action_file_new.set_sensitive(True)
            self.action_file_open.set_sensitive(True)
            self.action_file_close.set_sensitive(True)
            self.action_file_save.set_sensitive(True)
            self.action_file_save_as.set_sensitive(True)

        else:  # STATUS_FILE_NONE:
            self.action_project_new.set_sensitive(True)
            self.action_project_open.set_sensitive(True)
            self.action_workshop_preferences.set_sensitive(True)
            self.action_project_close.set_sensitive(True)

            self.action_file_new.set_sensitive(True)
            self.action_file_open.set_sensitive(True)
            self.action_file_close.set_sensitive(False)
            self.action_file_save.set_sensitive(False)
            self.action_file_save_as.set_sensitive(False)

    def get_status(self):
        return self.menu_status

    def _create_menu(self, window):
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

        # - 加入额外的检索Bar
        self.need_jump = NeedJump(True)

        self.search_entry = Gtk.SearchEntry()
        self.id_1 = self.search_entry.connect("search-changed", self.on_search_options_changed, self.need_jump)

        self.search_case_sensitive = Gtk.CheckButton.new_with_label("区分大小写")
        self.search_case_sensitive.set_active(True)
        self.id_2 = self.search_case_sensitive.connect("toggled", self.on_search_options_changed, self.need_jump)

        self.search_is_word = Gtk.CheckButton.new_with_label("单词")
        self.search_is_word.set_active(False)
        self.id_3 = self.search_is_word.connect("toggled", self.on_search_options_changed, self.need_jump)

        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 1)
        hbox.pack_start(self.search_entry, True, True, 10)
        hbox.pack_start(self.search_case_sensitive, True, True, 2)
        hbox.pack_start(self.search_is_word, True, True, 2)

        tool_item = Gtk.ToolItem()
        tool_item.add(hbox)
        self.toolbar.insert(tool_item, -1)  # 加在最后

        # 快捷菜单
        window.add_accel_group(self.uimanager.get_accel_group())

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

        action_project_new = Gtk.Action("ProjectNew", None, "New a Project", Gtk.STOCK_NEW)
        action_project_new.connect("activate", self.on_menu_project_new)
        action_group.add_action(action_project_new)
        self.action_project_new = action_project_new

        action_project_open = Gtk.Action("ProjectOpen", None, "Open a Project", Gtk.STOCK_OPEN)
        action_project_open.connect("activate", self.on_menu_project_open)
        action_group.add_action(action_project_open)
        self.action_project_open = action_project_open

        action_workshop_preferences = Gtk.Action("WorkshopPreferences", None, "Preferences", Gtk.STOCK_PREFERENCES)
        action_workshop_preferences.connect("activate", self.on_menu_workshop_setting)
        action_group.add_action(action_workshop_preferences)
        self.action_workshop_preferences = action_workshop_preferences

        action_project_close = Gtk.Action("ProjectClose", None, "Close Current Project", Gtk.STOCK_CLOSE)
        action_project_close.connect("activate", self.on_menu_project_close)
        action_group.add_action(action_project_close)
        self.action_project_close = action_project_close

        action_app_quit = Gtk.Action("AppQuit", None, None, Gtk.STOCK_QUIT)
        action_app_quit.connect("activate", self.on_menu_app_quit)
        action_group.add_action(action_app_quit)
        self.action_app_quit = action_app_quit

    def add_file_menu_actions(self, action_group):
        # File项目的菜单设定。
        action_filemenu = Gtk.Action("FileMenu", "File", None, None)
        action_group.add_action(action_filemenu)

        action_file_new = Gtk.Action("FileNew", None, "New a File", Gtk.STOCK_NEW)
        action_file_new.connect("activate", self.on_menu_file_open)
        action_group.add_action_with_accel(action_file_new, "<control>N")
        self.action_file_new = action_file_new

        action_file_open = Gtk.Action("FileOpen", None, "Open a file", Gtk.STOCK_OPEN)
        action_file_open.connect("activate", self.on_menu_file_open)
        action_group.add_action_with_accel(action_file_open, "<control>O")
        self.action_file_open = action_file_open

        action_file_close = Gtk.Action("FileClose", None, "Close current file", Gtk.STOCK_CLOSE)
        action_file_close.connect("activate", self.on_menu_file_close)
        action_group.add_action_with_accel(action_file_close, "<control>W")
        self.action_file_close = action_file_close

        action_file_save = Gtk.Action("FileSave", None, "Save current file", Gtk.STOCK_SAVE)
        action_file_save.connect("activate", self.on_menu_file_save)
        action_group.add_action_with_accel(action_file_save, "<control>S")
        self.action_file_save = action_file_save

        action_file_save_as = Gtk.Action("FileSaveAs", None, "Save current file as ...", Gtk.STOCK_SAVE_AS)
        action_file_save_as.connect("activate", self.on_menu_file_save_as)
        action_group.add_action(action_file_save_as)
        self.action_file_save_as = action_file_save_as

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

    def _jump_to_search_textbox_and_set_text(self, text):
        # 跳转到 SearchEntry中。
        # TODO 算是临时方案，首先设定为“”，然后再设定为需要的检索文字，这样就可以100%引发text_changed事件。
        if text is not None:
            self.search_entry.set_text("")
            self.search_entry.set_text(text)

        self.search_entry.grab_focus()

    def on_menu_project_new(self, widget):
        logging.debug("A Project|New menu item was selected.")
        self.on_menu_func(widget, self.ACTION_PROJECT_NEW)

    def on_menu_project_open(self, widget):
        logging.debug("A Project|Open menu item was selected.")
        self.on_menu_func(widget, self.ACTION_PROJECT_OPEN)

    def on_menu_workshop_setting(self, widget):
        logging.debug("A Project|Preferences menu item was selected.")
        self.on_menu_func(widget, self.ACTION_PROJECT_PREFERENCES)

    def on_menu_project_close(self, widget):
        logging.debug("A Project|Close menu item was selected.")
        self.on_menu_func(widget, self.ACTION_PROJECT_CLOSE)

    def on_menu_app_quit(self, widget):
        logging.debug("A App|Quit as menu item was selected.")
        self.on_menu_func(widget, self.ACTION_APP_QUIT)

    def on_menu_file_new(self, widget):
        logging.debug("A File|New menu item was selected.")
        self.on_menu_func(widget, self.ACTION_FILE_NEW)

    def on_menu_file_open(self, widget):
        logging.debug('A File|Open menu item was selected.')
        self.on_menu_func(widget, self.ACTION_FILE_OPEN)

    def on_menu_file_close(self, widget):
        logging.debug("A File|Close menu item was selected.")
        self.on_menu_func(widget, self.ACTION_FILE_CLOSE)

    def on_menu_file_save(self, widget):
        logging.debug("A File|Save menu item was selected.")
        self.on_menu_func(widget, self.ACTION_FILE_SAVE)

    def on_menu_file_save_as(self, widget):
        logging.debug("A File|Save as menu item was selected.")
        self.on_menu_func(widget, self.ACTION_FILE_SAVE_AS)

    def on_menuitem_active_send_service(self, widget, service):
        ''' 通用的菜单 Active 函数，发送service'''
        logging.debug("Common process of one menu item and send service.")
        FwManager.instance().requestService(service, None)

    def on_menuitem_active_with_search_text(self, widget, service):
        search_text = self.search_entry.get_text()
        FwManager.instance().requestService(service, {'text':search_text})

    def set_search_options(self, search_text, case_sensitive, is_word):
        # TODO ViewWindow 直接调用这个函数，存在问题！
        # 在此设置检索用的项目，想让 编辑器 显示检索项目，但是还不能跳转。下面是解决方法：（不优美）
        # 解决方法是引发事件的动作，放入一个 Object(不能是普通的数据)，然后在 on_search_options_changed 函数中，
        # 发送了信息后，再把此标志位改过来。

        self.need_jump.need = False

        if search_text is None:
            self.search_entry.set_text("")
        else:
            self.search_entry.set_text(search_text)
        self.search_case_sensitive.set_active(case_sensitive)
        self.search_is_word.set_active(is_word)

    def on_search_options_changed(self, widget, need_jump):
        search_text = self.search_entry.get_text()
        need_case_sensitive = self.search_case_sensitive.get_active()
        need_search_is_word = self.search_is_word.get_active()

        FwManager.instance().requestService('ctrl.search.find_text',
                    {'need_jump':need_jump.need, 'search_text':search_text, 'need_case_sensitive':need_case_sensitive, 'need_search_is_word':need_search_is_word})

        if need_jump.need is False:
            need_jump.need = True
