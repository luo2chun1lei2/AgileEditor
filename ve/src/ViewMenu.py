#-*- coding:utf-8 -*-

# 菜单和工具的模块。

import logging
from gi.repository import Gtk, Gdk, GtkSource

class NeedJump:
    def __init__(self, need):
        self.need = need

# 菜单的设定。
MENU_CONFIG = """
<ui>
    <menubar name='MenuBar'>
        <menu action='ProjectMenu'>
            <menuitem action='ProjectNew' />
            <menuitem action='ProjectOpen' />
            <menuitem action='ProjectPreferences' />
            <menuitem action='ProjectClose' />
            <separator />
            <menuitem action='ProjectUpdateTags' />
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
            <menuitem action='EditRedo' />
            <menuitem action='EditUndo' />
            <separator />
            <menuitem action='EditCut' />
            <menuitem action='EditCopy' />
            <menuitem action='EditPaste' />
            <menuitem action='EditDeleteLine' />
            <separator />
            <menuitem action='EditSelectAll' />
            <separator />
            <menuitem action='EditComment' />
            <menuitem action='EditUncomment' />
            <menuitem action='EditReplace' />
        </menu>
        <menu action='SearchMenu'>
            <menuitem action='SearchJumpTo' />
            <menuitem action='SearchFind' />
            <menuitem action='SearchFindNext' />
            <menuitem action='SearchFindInFiles' />
            <menuitem action='SearchFindPath' />
            <separator />
            <menuitem action='SearchDialogDefination' />
            <menuitem action='SearchDefination' />
            <menuitem action='SearchReference' />
            <menuitem action='SearchBackTag' />
            <separator />
            <menuitem action='SearchAddBookmark' />
            <menuitem action='SearchRemoveBookmark' />
        </menu>
        <menu action='HelpMenu'>
            <menuitem action='HelpInfo' />
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
        <toolitem action='SearchBackTag' />
    </toolbar>
</ui>
"""

class ViewMenu(object):
    # 管理菜单和工具栏
    
    # 当前的状态。
    (
     STATUS_PROJECT_NONE, # 没有打开的项目
     #STATUS_PROJECT_OPEN, # 打开了文件
     STATUS_FILE_NONE, # 项目已经打开，没有任何打开的文件
     STATUS_FILE_OPEN, # 项目已经打开，打开文件，且没有任何的修改。
     STATUS_FILE_OPEN_CHANGED, # 项目已经打开，文件打开状态，且已经有了修改。
    ) = range(4)
    
    # 可以发出的命令。 
    (
     ACTION_PROJECT_NEW,
     ACTION_PROJECT_OPEN,
     ACTION_PROJECT_PREFERENCES,
     ACTION_PROJECT_CLOSE,
     ACTION_PROJECT_UPDATE_TAGS,
     ACTION_APP_QUIT,
     
     ACTION_FILE_NEW,
     ACTION_FILE_OPEN,
     ACTION_FILE_CLOSE,
     ACTION_FILE_SAVE,
     ACTION_FILE_SAVE_AS,
     
     ACTION_EDIT_UNDO,
     ACTION_EDIT_REDO,
     
     ACTION_EDIT_CUT,
     ACTION_EDIT_COPY,
     ACTION_EDIT_PASTE,
     
     ACTION_EDIT_SELECT_ALL,
     
     ACTION_EDIT_DELETE_LINE,
     
     ACTION_EDIT_COMMENT,
     ACTION_EDIT_UNCOMMENT,
     ACTION_EDIT_REPLACE,
     
     ACTION_SEARCH_JUMP_TO,
     ACTION_SEARCH_FIND,            # 跳转到检索框
     ACTION_SEARCH_FIND_TEXT,       # 开始检索
     ACTION_SEARCH_FIND_NEXT,       # 跳转到下一个检索结果
     ACTION_SEARCH_FIND_IN_FILES,   # 在多个文件中检索等
     ACTION_SEARCH_FIND_PATH,       # 检索需要的文件路径
     
     ACTION_SEARCH_DIALOG_DEFINATION,
     ACTION_SEARCH_DEFINATION,
     ACTION_SEARCH_REFERENCE,
     ACTION_SEARCH_BACK_TAG,
     
     ACTION_SEARCH_ADD_BOOKMARK,
     ACTION_SEARCH_REMOVE_BOOKMARK,
     
     ACTION_HELP_INFO,
     
     # 其他地方的功能
     ACTION_EDITOR_SWITCH_PAGE,     # 切换当前编辑的文件
     ) = range(35)

    def __init__(self, window, on_menu_func):
        
        # 附件检索的控件
        self.search_entry = None
        
        self.on_menu_func = on_menu_func
        
        self._create_menu(window)
        
    def on_stub_menu_func(self, widget, action, param=None, param2=None, param3=None):
        pass
        
    def set_status(self, status):
        self.menu_status = status
            
        if self.menu_status == self.STATUS_PROJECT_NONE:
            self.action_project_new.set_sensitive(True)
            self.action_project_open.set_sensitive(True)
            self.action_project_preferences.set_sensitive(False)
            self.action_project_close.set_sensitive(False)
            
            self.action_file_new.set_sensitive(False)
            self.action_file_open.set_sensitive(False)
            self.action_file_close.set_sensitive(False)
            self.action_file_save.set_sensitive(False)
            self.action_file_save_as.set_sensitive(False)
              
        elif self.menu_status == self.STATUS_FILE_OPEN:
            
            self.action_project_new.set_sensitive(True)
            self.action_project_open.set_sensitive(True)
            self.action_project_preferences.set_sensitive(True)
            self.action_project_close.set_sensitive(True)
            
            self.action_file_new.set_sensitive(True)
            self.action_file_open.set_sensitive(True)
            self.action_file_close.set_sensitive(True)
            self.action_file_save.set_sensitive(False)
            self.action_file_save_as.set_sensitive(True)
            
        elif self.menu_status == self.STATUS_FILE_OPEN_CHANGED:
            self.action_project_new.set_sensitive(True)
            self.action_project_open.set_sensitive(True)
            self.action_project_preferences.set_sensitive(True)
            self.action_project_close.set_sensitive(True)
            
            self.action_file_new.set_sensitive(True)
            self.action_file_open.set_sensitive(True)
            self.action_file_close.set_sensitive(True)
            self.action_file_save.set_sensitive(True)
            self.action_file_save_as.set_sensitive(True)
        
        else: # STATUS_FILE_NONE:
            self.action_project_new.set_sensitive(True)
            self.action_project_open.set_sensitive(True)
            self.action_project_preferences.set_sensitive(True)
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

        uimanager = self.create_ui_manager()
        uimanager.insert_action_group(action_group)

        menubar = uimanager.get_widget("/MenuBar")
        
        self.menubar = menubar
        
        # 工具栏供
        toolbar = uimanager.get_widget("/ToolBar")
        
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
        toolbar.insert(tool_item, -1)   # 加在最后
        
        self.toolbar = toolbar
        
        # 快捷菜单
        window.add_accel_group(uimanager.get_accel_group())

        # 下面的弹出菜单
        #eventbox = Gtk.EventBox()
        #eventbox.connect("button-press-event", self.on_button_press_event)
        #box.pack_start(eventbox, True, True, 0)

        #label = Gtk.Label("Right-click to see the popup menu.")
        #eventbox.add(label)

        #self.popup = uimanager.get_widget("/PopupMenu")
        
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
        
        action_project_preferences = Gtk.Action("ProjectPreferences", None, "Preferences", Gtk.STOCK_PREFERENCES)
        action_project_preferences.connect("activate", self.on_menu_project_setting)
        action_group.add_action(action_project_preferences)
        self.action_project_preferences = action_project_preferences
        
        action_project_close = Gtk.Action("ProjectClose", None, "Close Current Project", Gtk.STOCK_CLOSE)
        action_project_close.connect("activate", self.on_menu_project_close)
        action_group.add_action(action_project_close)
        self.action_project_close = action_project_close
        
        action_project_update_tags = Gtk.Action("ProjectUpdateTags", None, "Update tags of Current Project", Gtk.STOCK_REFRESH)
        action_project_update_tags.connect("activate", self.on_menu_project_update_tags)
        action_group.add_action_with_accel(action_project_update_tags, "F5")
        self.action_project_update_tags = action_project_update_tags
        
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
            ("EditRedo", Gtk.STOCK_REDO, None, '<shift><control>Z', None, self.on_menu_edit_redo),
            ("EditUndo", Gtk.STOCK_UNDO, None, '<control>Z', None, self.on_menu_edit_undo),
            # 最好不要和控件缺省的快捷键冲突。
            #("EditCut", Gtk.STOCK_CUT, None, '<control>X', None, self.on_menu_edit_cut),
            #("EditCopy", Gtk.STOCK_COPY, None, '<control>C', None, self.on_menu_edit_copy),
            #("EditPaste", Gtk.STOCK_PASTE, None, '<control>V', None, self.on_menu_edit_paste),
            #("EditSelectAll", Gtk.STOCK_SELECT_ALL, None, '<control>A', None, self.on_menu_edit_select_all),
            ("EditCut", Gtk.STOCK_CUT, None, '', None, self.on_menu_edit_cut),
            ("EditCopy", Gtk.STOCK_COPY, None, '', None, self.on_menu_edit_copy),
            ("EditPaste", Gtk.STOCK_PASTE, None, '', None, self.on_menu_edit_paste),
            ("EditDeleteLine", Gtk.STOCK_DELETE, "Delete Line", '<control>D', None, self.on_menu_edit_delete_line),
            ("EditSelectAll", Gtk.STOCK_SELECT_ALL, None, '', None, self.on_menu_edit_select_all),
            ("EditComment", None, 'Comment', '<control>slash', None, self.on_menu_edit_comment),
            ("EditUncomment", None, 'Uncomment', '<control>question', None, self.on_menu_edit_uncomment),
            ("EditReplace", None, 'Replace', '<control>R', None, self.on_menu_edit_replace),
        ])
        
    def add_search_menu_actions(self, action_group):
        
        # JumpTo's accelerator is Ctrl+L
        # Find's accelerator is Ctrl+F
        
        action_group.add_actions([
            ("SearchMenu", None, "Search"),
            ("SearchJumpTo", Gtk.STOCK_JUMP_TO, None, '<control>L', None, self.on_menu_search_jumpto),
            ("SearchFind", Gtk.STOCK_FIND, None, "<control>F", None, self.on_menu_search_find),
            ("SearchFindNext", None, "Find Next", "<control>G", None, self.on_menu_search_find_next),
            ("SearchFindInFiles", Gtk.STOCK_FIND, "Find in files", "<control>H", None, self.on_menu_search_find_in_files),
            ("SearchFindPath", Gtk.STOCK_FIND, "Find path", "<shift><control>H", None, self.on_menu_search_find_path),
            ("SearchDialogDefination", None, 'Find definition by dialog', '<control>F3', None, self.on_menu_search_defination_by_dialog),
            ("SearchDefination", None, 'Definition', 'F3', None, self.on_menu_search_defination),
            ("SearchReference", None, 'Reference', 'F4', None, self.on_menu_search_reference),
            ("SearchBackTag", Gtk.STOCK_GO_BACK, 'Back Tag', '<shift><control>Left', None, self.on_menu_search_back_tag),
            ("SearchAddBookmark", Gtk.STOCK_GO_BACK, 'Add bookmark', '<control>B', None, self.on_menu_search_add_bookmark),
            ("SearchRemoveBookmark", Gtk.STOCK_GO_BACK, 'Remove bookmark', '<shift><control>B', None, self.on_menu_search_remove_bookmark),
        ])
        
    def add_help_menu_actions(self, action_group):
        # Help菜单设定。 
        action_helptmenu = Gtk.Action("HelpMenu", "Help", None, None)
        action_group.add_action(action_helptmenu)

        action_help_info = Gtk.Action("HelpInfo", None, "Information", Gtk.STOCK_INFO)
        action_help_info.connect("activate", self.on_menu_help_info)
        action_group.add_action_with_accel(action_help_info, "<Alt>H")
        self.action_help_info = action_help_info
        
    def create_ui_manager(self):
        
        uimanager = Gtk.UIManager()

        # Throws exception if something went wrong
        uimanager.add_ui_from_string(MENU_CONFIG)

        # Add the accelerator group to the toplevel window
        # accelgroup = uimanager.get_accel_group()
        # self.add_accel_group(accelgroup)
    
        return uimanager
    
    def on_menu_project_new(self, widget):
        logging.debug("A Project|New menu item was selected.")
        self.on_menu_func(widget, self.ACTION_PROJECT_NEW)
        
    def on_menu_project_open(self, widget):
        logging.debug("A Project|Open menu item was selected.")
        self.on_menu_func(widget, self.ACTION_PROJECT_OPEN)
        
    def on_menu_project_setting(self, widget):
        logging.debug("A Project|Preferences menu item was selected.")
        self.on_menu_func(widget, self.ACTION_PROJECT_PREFERENCES)
        
    def on_menu_project_close(self, widget):
        logging.debug("A Project|Close menu item was selected.")
        self.on_menu_func(widget, self.ACTION_PROJECT_CLOSE)
        
    def on_menu_project_update_tags(self, widget):
        logging.debug("A Project|Update Tags menu item was selected.")
        self.on_menu_func(widget, self.ACTION_PROJECT_UPDATE_TAGS)
    
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

    def on_menu_edit_redo(self, widget):
        logging.debug("A Edit|Redo as menu item was selected.")
        self.on_menu_func(widget, self.ACTION_EDIT_REDO)
    
    def on_menu_edit_undo(self, widget):
        logging.debug("A Edit|Undo as menu item was selected.")
        self.on_menu_func(widget, self.ACTION_EDIT_UNDO)

    def on_menu_edit_cut(self, widget):
        logging.debug("A Edit|Cut as menu item was selected.")
        self.on_menu_func(widget, self.ACTION_EDIT_CUT)
        
    def on_menu_edit_copy(self, widget):
        logging.debug("A Edit|Copy as menu item was selected.")
        self.on_menu_func(widget, self.ACTION_EDIT_COPY)

    def on_menu_edit_paste(self, widget):
        logging.debug("A Edit|Paste as menu item was selected.")
        self.on_menu_func(widget, self.ACTION_EDIT_PASTE)
        
    def on_menu_edit_select_all(self, widget):
        logging.debug("A Edit|Select All as menu item was selected.")
        self.on_menu_func(widget, self.ACTION_EDIT_SELECT_ALL)
        
    def on_menu_edit_delete_line(self, widget):
        logging.debug("A Edit|Delete Line All as menu item was selected.")
        self.on_menu_func(widget, self.ACTION_EDIT_DELETE_LINE)
        
    def on_menu_edit_comment(self, widget):
        logging.debug("A Edit|comment Line All as menu item was selected.")
        self.on_menu_func(widget, self.ACTION_EDIT_COMMENT)
    
    def on_menu_edit_uncomment(self, widget):
        logging.debug("A Edit|uncomment Line All as menu item was selected.")
        self.on_menu_func(widget, self.ACTION_EDIT_UNCOMMENT)
    
    def on_menu_edit_replace(self, widget):
        logging.debug("A Edit|replace Line All as menu item was selected.")
        self.on_menu_func(widget, self.ACTION_EDIT_REPLACE)
    
    def on_menu_search_jumpto(self, widget):
        logging.debug("A Search|JumpTo menu item was selected.")
        self.on_menu_func(widget, self.ACTION_SEARCH_JUMP_TO)
        
    def on_menu_search_find(self, widget):
        logging.debug("A Search|find menu item was selected.")
        # 跳转到 SearchEntry中。
        self.on_menu_func(widget, self.ACTION_SEARCH_FIND, self.search_entry)
        self.search_entry.grab_focus()
        
    def on_search_options_changed(self, widget, need_jump):
        search_text = self.search_entry.get_text()
        need_case_sensitive = self.search_case_sensitive.get_active()
        need_search_is_word = self.search_is_word.get_active()
        
        self.on_menu_func(self.search_entry, self.ACTION_SEARCH_FIND_TEXT, need_jump.need, search_text, need_case_sensitive, need_search_is_word)
        
        if need_jump.need is False:
            need_jump.need = True
    
    def on_menu_search_find_next(self, widget):
        logging.debug("A Search|find next menu item was selected.")
        search_text = self.search_entry.get_text()
        self.on_menu_func(widget, self.ACTION_SEARCH_FIND_NEXT, search_text)
    
    def on_menu_search_find_in_files(self, widget):
        logging.debug("A Search|find in files menu item was selected.")
        self.on_menu_func(widget, self.ACTION_SEARCH_FIND_IN_FILES)
        
    def on_menu_search_find_path(self, widget):
        logging.debug("A Search|find path menu item was selected.")
        self.on_menu_func(widget, self.ACTION_SEARCH_FIND_PATH)
        
    def on_menu_search_defination_by_dialog(self, widget):
        logging.debug("A Search|find defination by dialog menu item was selected.")
        self.on_menu_func(widget, self.ACTION_SEARCH_DIALOG_DEFINATION)
    
    def on_menu_search_defination(self, widget):
        logging.debug("A Search|defination menu item was selected.")
        self.on_menu_func(widget, self.ACTION_SEARCH_DEFINATION)
        
    def on_menu_search_reference(self, widget):
        logging.debug("A Search|reference menu item was selected.")
        self.on_menu_func(widget, self.ACTION_SEARCH_REFERENCE)
        
    def on_menu_search_back_tag(self, widget):
        logging.debug("A Search|back tag menu item was selected.")
        self.on_menu_func(widget, self.ACTION_SEARCH_BACK_TAG)
        
    def on_menu_search_add_bookmark(self, widget):
        logging.debug("A Search|Add bookmark menu item was selected.")
        self.on_menu_func(widget, self.ACTION_SEARCH_ADD_BOOKMARK)
        
    def on_menu_search_remove_bookmark(self, widget):
        logging.debug("A Search|Remove bookmark menu item was selected.")
        self.on_menu_func(widget, self.ACTION_SEARCH_REMOVE_BOOKMARK)

    def on_menu_help_info(self, widget):
        logging.debug("A Help|Infomation as menu item was selected.")
        self.on_menu_func(widget, self.ACTION_HELP_INFO)
        
    def set_search_options(self, search_text, case_sensitive, is_word):
        
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
        