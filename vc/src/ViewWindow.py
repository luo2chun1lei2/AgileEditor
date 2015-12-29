#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys, getopt, shutil
from gi.repository import Gtk, Gdk, GtkSource, GLib, Pango

from ViewMenu import *
from ViewDialog import *
from ViewMultiPages import *
from ViewCmdGroupTree import *
from ViewLog import *
from ViewHelp import ViewDialogInfo

# 主窗口
class ViewWindow(Gtk.Window):
    
    '''
    ideWorkshop:ModelWorkshop:当前的workshop。
    cur_prj:ModelProject:当前打开的项目。
    '''
    
    ###################################
    ## 返回值的定义
    RLT_OK = 0          # 正常
    RLT_CANCEL = 1      # 取消
    RLT_ERROR = 2       # 错误
    
    PROGRAM_NAME='Visual Command 版本 0.1 '
    
    '''
    总窗口。
    '''
    def __init__(self, workshop_dir):
        
        self.workshop_dir = workshop_dir
        
        # 创建画面
        self._create_layout()
        
    ###########################################################################
    ## 创建画面
    
    def _create_layout(self):
        '''
        创建画面。
        '''
        Gtk.Window.__init__(self, title=self.PROGRAM_NAME)

        # 总的布局器
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # 菜单和工具栏
        self.ide_menu = ViewMenu(self, self.on_menu_func)
        vbox.pack_start(self.ide_menu.menubar, False, False, 0)
        vbox.pack_start(self.ide_menu.toolbar, False, False, 0)
        
        # 左右布局器：命令组列表和命令编辑器
        # - resize:子控件是否跟着paned的大小而变化。
        # - shrink:子控件是否能够比它需要的大小更小。
        
        # 左右布局器：命令组列表、命令组
        panedListAndCmdGp = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
         
        # 命令组列表
        container, self.cmdgroupList = self._create_cmdgrp_list()
        panedListAndCmdGp.pack1(container, resize=False, shrink=True)
        
        # 打开的命令组内命令列表（多个列表的切换Tab）
        self.mutilePages = ViewMultiPages(self.on_menu_func)
        self.tab_page = self.mutilePages.get_notebook()
        
        panedListAndCmdGp.pack2(self.tab_page, resize=True, shrink=True)
        
        # 设定divider的位置.
        panedListAndCmdGp.set_position(400);
        
        vbox.pack_start(panedListAndCmdGp, True, True, 5)
                
        # - 加入布局器。
        self.add(vbox)
        
    def _create_cmdgrp_list(self):
        ''' 创建包含命令组的列表(实际上是Tree来实现的)。 '''
        
        vc_cmd_groups = VcCmdGroupMng.instance().cmd_groups
        cmdgroupTree = ViewCmdGroupTree(self.on_menu_func, vc_cmd_groups)
        
        return cmdgroupTree.scrolledWindow, cmdgroupTree

    ###########################################################################
    ## 回调方法
    
    def on_menu_func(self, widget, action, param=None):
        ''' 从菜单等过来的命令，在这里执行。'''
        
        if action == ViewMenu.ACTION_APP_QUIT:
            self.ide_quit(widget)
        
        elif action == ViewMenu.ACTION_COMMAND_GROUP_NEW:   # 添加一个命令组
            self.ide_new_command_group()
        elif action == ViewMenu.ACTION_COMMAND_GROUP_OPEN:  # 显示一个命令组
            self.ide_open_command_group(param.get_key())
        elif action == ViewMenu.ACTION_COMMAND_GROUP_CLOSE: # 不显示一个命令组
            if param is None:
                name = None
            else:
                name = param.get_key()
            self.ide_close_command_group(name)
        elif action == ViewMenu.ACTION_COMMAND_GROUP_SAVE:  # 保存一个命令组
            self.ide_save_command_group()
        elif action == ViewMenu.ACTION_COMMAND_GROUP_DELETE:    # 删除一个命令组
            self.ide_delete_command_group()
        
        elif action == ViewMenu.ACTION_COMMAND_ADD:    # 向命令组中添加一个命令
            self.ide_add_cmd()
        elif action == ViewMenu.ACTION_COMMAND_DELETE: # 删除一个命令
            self.ide_del_cmd()
        elif action == ViewMenu.ACTION_COMMAND_MODIFY: # 想修改一个命令        -- 不需要
            pass
        elif action == ViewMenu.ACTION_COMMAND_UP:     # 将命令在命令组中的位置提高一个
            self.ide_move_up_cmd()
        elif action == ViewMenu.ACTION_COMMAND_DOWN:   # 将命令在命令组中的位置降低一个
            self.ide_move_down_cmd()
            
        elif action == ViewMenu.ACTION_HELP_INFO:
            self.ide_help_info()
        
        else:
            print 'Unknown action %d' % action
            
    def on_src_buffer_changed(self, widget):
        ''' 当文件发了变化后。'''
        self._set_status(ViewMenu.STATUS_FILE_OPEN_CHANGED)
    
    ###################################
    ## 基础功能实现
    
    def ide_quit(self, widget):
        '''
        如果打开了当前文件，且修改过了，需要保存。
        关闭当前文件。
        退出程序。
        '''
        
        result = self.ide_close_command_group(widget)
        if result != self.RLT_OK:
            return result
        
        Gtk.main_quit()
        
    def ide_new_command_group(self):
        ''' 生成一个新的命令组 '''
        dlg_response, cmd_grg_name = ViewDialogNewCommandGroup.show(self)
        if dlg_response != Gtk.ResponseType.OK:
            return False
        
        # 显示在左边的列表中。
        self.cmdgroupList.add_new_cmd_grp(cmd_grg_name)
        
    def ide_open_command_group(self, cmdgroup_name):
        # 打开指定的命令组编辑器
        self.mutilePages.show_command_group(cmdgroup_name)
        
    def ide_close_command_group(self, name):
        # 关闭目前正在打开的命令组编辑器
        self.mutilePages.close_command_group(name)

    def ide_save_file(self, widget):
        '''
        如果当前文件已经打开，并且已经修改了，就保存文件。
        '''
        
        print('ide save file')
        
        ide_editor = self.multiEditors.get_current_ide_editor()
        if ide_editor is None:
            print('No file is being opened.')
            return self.RLT_OK
        
        src_buffer = ide_editor.cmdList.get_buffer()
        if src_buffer.get_modified():
            if ide_editor.ide_file.file_path is None:
                dialog = Gtk.FileChooserDialog("请选择一个文件", self,
                           Gtk.FileChooserAction.SAVE ,
                           (    Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                Gtk.STOCK_OK, Gtk.ResponseType.OK))

                response = dialog.run()
                file_path = dialog.get_filename()
                dialog.reset_state()
                
                if response == Gtk.ResponseType.OK:
                    print("File selected: " + file_path)
                    
                    # 打开一个空的文件，或者里面已经有内容了。
                    ide_editor.ide_file.open_file(file_path)
                    self._set_src_language(src_buffer, file_path)

                elif response == Gtk.ResponseType.CANCEL:
                    print("Cancel to save one file.")
                    return self.RLT_CANCEL

            # 将内容保存到文件中。
            ide_editor.ide_file.save_file(self._ide_get_editor_buffer())
            src_buffer.set_modified(False)
            print('ide save file to disk file.')
        
        self._set_status(ViewMenu.STATUS_FILE_OPEN)
        
        return self.RLT_OK
        
    def ide_save_as_file(self, widget):
        '''
        显示对话框，选择另存为的文件名字。
        然后关闭当前文件，
        创建新的Ide文件，打开这个文件，并保存。
        '''
        print("ide save as other file.")
        
        ide_editor = self.multiEditors.get_current_ide_editor()
        old_file_path = self.multiEditors.get_current_abs_file_path()
        
        if ide_editor.ide_file == None:
            print('No file is being opened')
            return self.RLT_OK
        
        # 如果是新文件，则按照Save的逻辑进行
        src_buffer = self._ide_get_editor_buffer()
        if src_buffer.get_modified():
            if ide_editor.ide_file.file_path is None:
                return self.ide_save_file(widget)

        # 如果是已经打开的文件，就将当前文件保存成新文件后，关闭旧的，打开新的。
        # 设定新的文件路径   
        dialog = Gtk.FileChooserDialog("请选择一个文件", self, \
                                               Gtk.FileChooserAction.SAVE , \
                                               (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, \
                                                Gtk.STOCK_OK, Gtk.ResponseType.OK))

        response = dialog.run()
        file_path = dialog.get_filename()
        dialog.reset_state()

        if response == Gtk.ResponseType.CANCEL:
            print("Cancel to save as one file.")
            return self.RLT_CANCEL
        
        print("File selected: " + file_path)
        
        # 将当前文件保存成新文件
        shutil.copy(old_file_path, file_path)
        
        # 关闭原来的文件。
        # ide_editor.ide_file.close_file()
        self.multiEditors.close_editor(old_file_path)
        
        # 打开指定的文件，并保存       
        #self.current_idefile = ModelFile()
#         ide_editor.ide_file.open_file(file_path)
#         
#         ide_editor = self.multiEditors.get_current_ide_editor()
#         src_buffer = self._ide_get_editor_buffer()
#         self.current_idefile.save_file(src_buffer)
#         self._set_src_language(src_buffer, file_path)
#         src_buffer.set_modified(False)

        self.multiEditors.show_editor(file_path)
        
        # 切换当前的状态
        self._set_status(ViewMenu.STATUS_FILE_OPEN)
        
    
        
    def ide_help_info(self):
        dialog = ViewDialogInfo(self)
        dialog.run()
        
        dialog.destroy()
        
    def ide_edit_redo(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return
        
        src_buffer = ve_editor.cmdList.get_buffer()
        src_buffer.redo()
    
    def ide_edit_undo(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return
        
        src_buffer = ve_editor.cmdList.get_buffer()
        src_buffer.undo()
        
    def ide_edit_cut(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return
        
        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = ve_editor.cmdList.get_clipboard(atom)
        ve_editor.cmdList.get_buffer().cut_clipboard(clipboard, True)
        
    def ide_edit_copy(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return
        
        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = ve_editor.cmdList.get_clipboard(atom)
        ve_editor.cmdList.get_buffer().copy_clipboard(clipboard)
        
    def ide_edit_paste(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return
        
        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = ve_editor.cmdList.get_clipboard(atom)
        ve_editor.cmdList.get_buffer().paste_clipboard(clipboard, None, True)
    
    def ide_edit_select_all(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return
        
        src_buffer = ve_editor.cmdList.get_buffer()
        src_buffer.select_range(src_buffer.get_start_iter(), src_buffer.get_end_iter())
        
    def ide_switch_page(self, abs_file_path):
        '''
        abs_file_path string 切换到的文件名字
        '''
        
        self.multiEditors.show_editor(abs_file_path)
        
        view_editor = self.multiEditors.get_editor_by_path(abs_file_path)
        self._ide_search_init(view_editor.cmdList.get_buffer())
            
        # 分析标记
        if self.cur_prj is not None:
            tags = self.cur_prj.query_tags_by_file(abs_file_path)
            self.ide_refresh_file_tag_list(tags)
            
        # 显示文件的路径。
        self.ide_set_title(abs_file_path)
        
        # 在文件树那里同步
        self.cmdgroupList.show_file(abs_file_path)
    
    ###########################################################################
    ## 最底层的功能
    
    def _add_filters(self, dialog):
        ''' 给对话框加入过滤器 '''
        # TODO:以后应该可以打开任意文件，然后根据后缀进行判断。
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_c = Gtk.FileFilter()
        filter_c.set_name("C/Cpp/hpp files")
        filter_c.add_mime_type("text/x-c")
        dialog.add_filter(filter_c)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("Python files")
        filter_py.add_mime_type("text/x-python")
        dialog.add_filter(filter_py)

#         filter_any = Gtk.FileFilter()
#         filter_any.set_name("Any files")
#         filter_any.add_pattern("*")
#         dialog.add_filter(filter_any)

    def _set_src_language(self, src_buffer, file_path):
        manager = GtkSource.LanguageManager()
        
        if file_path is not None:
            language = manager.guess_language(file_path, None)        # 设定语法的类型
            src_buffer.set_language(language)
        else:
            src_buffer.set_language(None)
        
        return src_buffer
    
    def _set_status(self, status):
#         if self.current_idefile is None:
#             self.set_title(self.PROGRAM_NAME)
#         else:
#             if self.current_idefile.file_path is None:
#                 self.set_title(self.PROGRAM_NAME + ' New')
#             else:
#                 self.set_title(self.PROGRAM_NAME + ' ' + self.current_idefile.file_path)
        self.ide_set_title()

    def ide_set_title(self, title = ''):
        self.set_title(self.PROGRAM_NAME + ' ' + title)

        #TODO:不让状态变化。
        #self.ide_menu.set_status(status)
        self.ide_menu.set_status(ViewMenu.STATUS_FILE_OPEN_CHANGED)
        
    def ide_refresh_file_tag_list(self, tags):
        ''' 根据Tag的列表，更新文件对应的Tag列表
        tags:[IdeOneTag]:Tag列表。
        '''
        self.ideTagList.set_model(tags)
        
    def ide_goto_line(self, line_number):
        ''' 跳转到当前文件的行。
        line_number:int:行号（从1开始）
        '''
        #print 'goto line number:', line_number
        text_buf = self._ide_get_editor_buffer()
        it = text_buf.get_iter_at_line(line_number-1)
        
        text_buf.place_cursor(it)
        
        # 设定光标的位置，和什么都没有选中
        text_buf.select_range(it, it)
        # 屏幕滚动到这个地方。
        editor = self.multiEditors.get_current_editor()
        editor.scroll_to_iter(it, 0.25, False, 0.0, 0.5)
        
        # TODO:这里不是错误，而是给threads_add_idle返回不再继续调用的设定。
        return False
    
    def ide_editor_set_focus(self):
        ''' 获取焦点(延迟调用) '''
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self._ide_editor_set_focus)
    
    def _ide_editor_set_focus(self):
        ''' 获取焦点 '''
        editor = self.multiEditors.get_current_editor()
        editor.grab_focus()
    
    def ide_goto_file_line(self, file_path, line_number):
        ''' 跳转到指定文件的行。 '''
        # 先找到对应的文件
        # 然后再滚动到指定的位置
        #print 'jump to path:' + file_path + ', line:' + str(line_number)
        if self.ide_open_file(None, file_path) == self.RLT_OK:
            # 注意：这里采用延迟调用的方法，来调用goto_line方法，可能是buffer被设定后，
            # 还有其他的控件会通过事件来调用滚动，所以才造成马上调用滚动不成功。
            Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.ide_goto_line, line_number)
    
    def ide_search_defination(self):
        ''' 查找定义
        '''
        tag_name = self._ide_get_selected_text_or_word()
        tags = self.cur_prj.query_defination_tags(tag_name)
        
        if len(tags) == 0:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, \
                                       Gtk.ButtonsType.OK, "没有找到对应的定义。")
            dialog.run()
            dialog.reset_state()
            
        elif len(tags) == 1:
            ''' 直接跳转。 '''
            tag = tags[0]
            self.ide_goto_file_line(tag.tag_file_path, tag.tag_line_no)
        else:
            ''' 显示列表，让使用者挑选一个 '''
            tag = ViewDialogTagsOpen.show(self, tags)
            if tag:
                self.ide_goto_file_line(tag.tag_file_path, tag.tag_line_no)
    
    def ide_search_reference(self):
        ''' 查找引用
        '''
        tag_name = self._ide_get_selected_text_or_word()
        tags = self.cur_prj.query_reference_tags(tag_name)
        
        if len(tags) == 0:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, \
                                       Gtk.ButtonsType.OK, "没有找到对应的引用。")
            dialog.run()
            dialog.reset_state()
            
        elif len(tags) == 1:
            ''' 直接跳转。 '''
            tag = tags[0]
            self.ide_goto_file_line(tag.tag_file_path, tag.tag_line_no)
        else:
            ''' 显示列表，让使用者挑选一个 '''
            tag = ViewDialogTagsOpen.show(self, tags)
            if tag:
                self.ide_goto_file_line(tag.tag_file_path, tag.tag_line_no)
    
    def ide_jump_to(self, line_number):
        self.ide_goto_line(line_number)
    
    def ide_find(self, search_entry):
        '''
        如果当前编辑器中有选中的文字，就将此文字放入检索本中。
        search_text string 需要检索的文字
        '''
        view_editor = self.multiEditors.get_current_ide_editor()
        if view_editor is None:
            return
        
        buf = view_editor.cmdList.get_buffer()
         
        if not buf.get_has_selection():
            return
         
        (start, end) = buf.get_selection_bounds()
         
        text = buf.get_text(start, end, False)

        search_entry.set_text(text)
    
    def _ide_search_init(self, text_buffer):
        self.search_text = None
        
        self.search_setting = GtkSource.SearchSettings.new()
        self.search_setting.set_regex_enabled(True)
        self.search_setting.set_case_sensitive(False)
        self.search_setting.set_wrap_around(True)
        
        self.search_context = GtkSource.SearchContext.new(text_buffer, self.search_setting)
        self.search_context.set_highlight(True)
        
    def _ide_search_text(self, text_buffer, search_text):
        
        self.search_context.get_settings().set_search_text(search_text)
        
        # -从当前的位置查找
        mark = text_buffer.get_insert()
        ite = text_buffer.get_iter_at_mark(mark)
        
        found, start_iter, end_iter = self.search_context.forward(ite)
        
        # 如果找到，就跳转到下面最近位置
        if found:
            line_num = start_iter.get_line()
            self.ide_jump_to(line_num)
    
    def _ide_search_text_next(self, text_buffer, search_text):
        # -从新位置查找
        mark = text_buffer.get_insert()
        ite = text_buffer.get_iter_at_mark(mark)
        
        found, start_iter, end_iter = self.search_context.forward(ite)
        
        # 如果找到，就跳转到下面最近位置
        if found:
            line_num = start_iter.get_line()
            self.ide_jump_to(line_num)
            
            text_buffer.move_mark_by_name("selection_bound", start_iter)
            text_buffer.move_mark_by_name("insert", end_iter)
            
    def ide_find_text(self, search_text):
        view_editor = self.multiEditors.get_current_ide_editor()
        if view_editor is None:
            return
        
        self._ide_search_text(view_editor.cmdList.get_buffer(), search_text)
        
    def ide_find_next(self, search_text):
        '''
        如果当前编辑器中有选中的文字，则直接显示对话框。
        对话框中的文字，缺省被选中，可以被全文粘贴。
        然后查找定义。 
        search_text string 需要检索的文字
        '''
        view_editor = self.multiEditors.get_current_ide_editor()
        if view_editor is None:
            return

        self._ide_search_text_next(view_editor.cmdList.get_buffer(), search_text)
        
    def ide_find_in_files(self):
        '''
        在多个文件中检索，比如文件夹内检索，打开的文件中检索，或者项目中检索等。
        '''
    
    def _ide_get_selected_text_or_word(self):
        ''' 从编辑器中得到当前被选中的文字，
        如果没有就返回光标所在的单词，
        如果都无法达到，就返回None 
        '''
        text_buf = self._ide_get_editor_buffer()
        selection = text_buf.get_selection_bounds()
        
        text = None
        if len(selection) > 0:
            # 已经有选中的文字。
            start, end = selection
            text = text_buf.get_text(start, end, False)
        else:
            
            # 没有选中任何的文字
            mark = text_buf.get_insert()
            word_start = text_buf.get_iter_at_mark(mark)
            word_end = text_buf.get_iter_at_mark(mark)

            # 得到以空格为区分的单词开头。
            while True:
                if word_start.starts_word():
                    n = word_start.copy()
                    # 获得前一个字符。
                    if not n.backward_char():
                        break
                    # 这里的算法应该有问题，如果判断为 空格，则不无法通过，不明白为什么？
                    if text_buf.get_text(n, word_start, False) != "_":
                        break
                    
                word_start.backward_word_start()
            
            # 得到以空格为区分的单词结尾。
            while True:
                if word_end.ends_word():
                    n = word_end.copy()
                    if not n.forward_char():
                        break
                    if text_buf.get_text(word_end, n, False) != "_":
                        break
                    
                word_end.forward_word_end()
                
            text = text_buf.get_text(word_start, word_end, False)
            
        print 'selected text or word is "', text, '"'

        return text
    
    def _ide_set_completion(self, ideProject):
        ''' 设定当前的编辑器的单词补足，当切换不同的Project时，才有必要 '''
        
        # 单词补齐，使用CompletionWords

        #配置单词自动补齐，使用自定义的CompletionProvider
        editor = self.multiEditors.get_current_editor()
        completion = cmdList.props.completion
        
        # 清除之前的所有provider
        providers = completion.get_providers()
        for p in providers:
            completion.remove_provider(p)

        # 加入新的Provider
        completion.add_provider(ideProject.get_completion_provider())

    def _ide_get_editor_buffer(self):
        editor = self.multiEditors.get_current_editor()
        if editor is None:
            return None
        
        return editor.get_buffer()

    def ide_add_cmd(self):
        # 在当前位置添加一个命令。
        ide_editor = self.mutilePages.get_current_ide_editor()
        viewPage = ide_editor.view
        viewPage.add_cmd()
    
    def ide_del_cmd(self):
        # 删除当前位置的命令。
        ide_editor = self.mutilePages.get_current_ide_editor()
        viewPage = ide_editor.view
        viewPage.del_cmd()
    
    def ide_move_up_cmd(self):
        # 将当前命令向上移动一个位置
        ide_editor = self.mutilePages.get_current_ide_editor()
        viewPage = ide_editor.view
        viewPage.move_up_cmd()
    
    def ide_move_down_cmd(self):
        # 将当前命令向下移动一个位置
        ide_editor = self.mutilePages.get_current_ide_editor()
        viewPage = ide_editor.view
        viewPage.move_down_cmd()
        