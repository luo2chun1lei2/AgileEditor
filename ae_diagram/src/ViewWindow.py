#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys, shutil
from gi.repository import Gtk, Gdk, GtkSource, GLib, Pango

from ViewMenu import *
from VgModel import *
from VgUtils import *

# 主窗口
class ViewWindow(Gtk.Window):
    
    '''
    ideWorkshop:ModelWorkshop:当前的workshop。
    cur_prj:ModelProject:当前打开的项目。
    '''
    
    ###################################
    ## 返回值的定义
    
    RLT_OK=0
    RLT_CANCEL=1    # 取消
    RLT_ERROR=2     # 错误
    
    PROGRAM_NAME='Visual Editor '
    
    '''
    总窗口。
    '''
    def __init__(self):
        # 创建画面
        self._create_layout()
        self._init_data()
        
    def _create_layout(self):
        ''' 创建画面。 '''
        Gtk.Window.__init__(self, title=self.PROGRAM_NAME)

        # 设定窗口的大小。
        # TODO:应该记住上一次的大小
        self.set_default_size(800, 900)
        
        # 窗口的布局器
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # 创建内部的控件。
        # - 菜单和工具栏
        self.ide_menu = ViewMenu(self, self.on_process_func)
        vbox.pack_start(self.ide_menu.menubar, False, False, 0)
        vbox.pack_start(self.ide_menu.toolbar, False, False, 0)
        
        # 产生棋盘
        self.create_game_panel()
        self.grid_game.set_size_request(600, 600)
        
        vbox.pack_start(self.grid_game, True, True, 5)
        vbox.show()

        # - 加入布局器。
        self.add(vbox)
        
    def create_game_panel(self):
        self.grid_game = Gtk.Grid()
        
        vg_model = VgModel.instance()
        vg_model.create(10, 10)
        
        for r in range(0, vg_model.n_row):
            for c in range(0, vg_model.n_col):
                btn = self.create_one_view_piece(r+1, c+1)
                #btn.set_label("%d,%d" % (r+1, c+1))
                self.grid_game.attach(btn, c, r, 1, 1)
                
        self.refresh_by_mode(vg_model)
        
    def get_view_piece(self, row, col):
        return self.grid_game.get_child_at(col-1, row-1) 
        
    def create_one_view_piece(self, row, col):
        btn = Gtk.Button()
        btn.set_label("")
        
        btn.set_vexpand(True)
        btn.set_hexpand(True)
        
        btn.connect('clicked', self.on_click_piece, row, col)
        
        return btn
    
    def on_click_piece(self, button, row, col):
        vg_model = VgModel.instance()
        if vg_model.change_selected(row, col):
            self.refresh_by_mode(vg_model)
    
    def refresh_by_mode(self, vg_model):
        vg_model = VgModel.instance()
        
        for r in range(0, vg_model.n_row):
            row = r + 1
            for c in range(0, vg_model.n_col):
                col = c + 1
                mdl_piece = vg_model.get_piece(row, col)
                view_piece = self.get_view_piece(row, col)
                
                if mdl_piece.state == VgPiece.STATE_EMPTY:
                    view_piece.set_visible(False)
                elif mdl_piece.state == VgPiece.STATE_SELECTED:
                    view_piece.set_visible(True)
                    view_piece.set_label(mdl_piece.get_text())
                    view_piece.set_relief(Gtk.ReliefStyle.NORMAL)
                elif mdl_piece.state == VgPiece.STATE_UNSELECTED:
                    view_piece.set_visible(True)
                    view_piece.set_label(mdl_piece.get_text())
                    view_piece.set_relief(Gtk.ReliefStyle.NONE)
    
    ###################################
    ## 创建画面

    def _init_data(self):
        # 取得剪贴板
        return
        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = self.get_clipboard(atom)
        
        clipboard.request_text(self.on_get_text_from_clipboard)
        
    def on_get_text_from_clipboard(self, clipboard, text):
        source_cmd = VgPiece(text, None)
        clipboard.clear()
        
        VgModel.add(source_cmd)
        self.show_source_cmd(source_cmd)
        
    def show_source_cmd(self, source_cmd):
        self.history_list.refresh_model()
        
        self.set_source(source_cmd.source)
        self.set_command(source_cmd.command)
        
    def set_command_alert(self, alert):
        ''' 改变控件的颜色。'''
        
        buf = self.txt_command.get_buffer()
        if alert:
            tag = self.tag_cmd_err
        else:
            tag = self.tag_cmd_ok
            
        buf.apply_tag(tag, buf.get_start_iter(), buf.get_end_iter())
        
    def set_source(self, text):
        if text is None:
            self.txt_source.get_buffer().set_text("")
        else:
            self.txt_source.get_buffer().set_text(text)
        
    def set_command(self, text):
        if text is None:
            self.txt_command.get_buffer().set_text("")
        else:
            self.txt_command.get_buffer().set_text(text)
        
    def _copy_result_2_clipboard(self):
        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = self.get_clipboard(atom)
        
        buf = self.txt_source.get_buffer()
        text = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False)
        clipboard.set_text(text, len(text))
    
    ###################################
    ## 回调方法
    def on_process_func(self, widget, action, param=None):
        if action == ViewMenu.ACTION_DISCARD:
            # 退出程序，结果也不需要保存。
            self.vx_quit()
            
        elif action == ViewMenu.ACTION_APPLY:
            # 退出程序，但是当前结果放入到剪贴板中。
            self.vx_save_and_quit()
            
        elif action == ViewMenu.ACTION_EXECUTE:
            # 执行命令。
            self.ide_execute_cmd()
        elif action == ViewMenu.ACTION_KEEP:
            # 将当前结果放入到命令历史记录中。
            self.ide_close_command_group()
        elif action == ViewMenu.ACTION_UNDO:
            # 回退到上一个命令运行情况。
            self.ide_undo_execute()
        elif action == ViewMenu.ACTION_RESTORE:
            # 回退到最开始的状况。
            self.ide_restore_execute()
            
        elif action == ViewMenu.ACTION_BACK_TO:
            self.ide_back_to_source_cmd(param)
                        
        elif action == ViewMenu.ACTION_HELP_INFO:
            # 显示帮助信息。
            self.ide_help_info()
        
        else:
            print 'Unknown action %s' % (action)
            
    def on_src_bufer_changed(self, widget):
        ''' 当文件发了变化后。'''
        self._set_status(ViewMenu.STATUS_FILE_OPEN_CHANGED)
        
    def on_tree_source_cmd_selection_changed(self, selection):
        ''' 文件列表选择时，不是双击，只是选择变化时 '''
        #model, treeiter = selection.get_selected()
        #if treeiter != None:
        #    print "You selected", model[treeiter][1]
        pass
    
    def on_tree_source_cmd_row_activated(self, treeview, tree_path, column):
        ''' 双击了文件列表中的项目。
        如果是文件夹，就将当前文件夹变成这个文件夹。
        如果是文件，就打开。
        '''
        model = treeview.get_model()
        pathname = model._get_fp_from_tp(tree_path)
        abs_path = model.get_abs_filepath(pathname)
        
        if not os.access(abs_path, os.R_OK):
            print '没有权限进入此目录。'
            return
        
        if model.is_folder(tree_path):
            #new_model = FsTreeModel(abs_path)
            #treeview.set_model(new_model)
            
            #self.window.set_title(new_model.dirname)
            
            treeview.expand_row(tree_path, False)
        else:
            # 根据绝对路径显示名字。
            self.ide_open_file(None, abs_path)
    
    ###################################
    ## 基本功能
    
    def vx_quit(self):        
        Gtk.main_quit()
        
    def vx_save_and_quit(self):
        self._copy_result_2_clipboard()
        Gtk.main_quit()
        
    def ide_execute_cmd(self):
        
        buf = self.txt_command.get_buffer()
        str_cmd = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False)
        if is_empty(str_cmd):
            return
        
        buf = self.txt_source.get_buffer()
        str_source = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False)
        
        vx_source_cmd = VgModel.last()
        vx_source_cmd.command = str_cmd
        vx_source_cmd.source = str_source
        return_source_cmd = VxExecute.execute_cmd(vx_source_cmd)
        
        if return_source_cmd is not None:
            VgModel.add(return_source_cmd)
            self.show_source_cmd(return_source_cmd)
            self.set_command_alert(False)
        else:
            self.set_command_alert(True)
            
    def ide_undo_execute(self):
        if VgModel.len() == 1:
            return
        
        VgModel.pop()
        vx_source_cmd = VgModel.last()
        
        self.show_source_cmd(vx_source_cmd)
    
    def ide_restore_execute(self):
        if VgModel.len() == 1:
            return
        
        VgModel.pop()
        vx_source_cmd = VgModel.last()
        
        self.show_source_cmd(vx_source_cmd)
        
    def ide_back_to_source_cmd(self, vx_source_cmd):
        if VgModel.len() == 1:
            return
        
        VgModel.pop_to(vx_source_cmd)
        vx_source_cmd = VgModel.last()
        
        self.show_source_cmd(vx_source_cmd)
            
    def ide_open_command(self, widget, path=None):
        '''
        如果已经打开文件，关闭当前文件
        显示“挑选”文件。
        然后显示打开的文件。
        path:string:绝对路径。
        '''
        result = self.RLT_CANCEL
        
        if(path is None):
            dialog = Gtk.FileChooserDialog("请选择一个文件", self,
                    Gtk.FileChooserAction.OPEN,
                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                     Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    
            self._add_filters(dialog)
    
            response = dialog.run()
            
            file_path = dialog.get_filename()
            dialog.reset_state()
        else:
            response = Gtk.ResponseType.OK
            file_path = path
        
        if response == Gtk.ResponseType.OK:
            print("File selected: " + file_path)
            
#             self.multiEditors.show_editor(file_path)
#             
#             view_editor = self.multiEditors.get_editor_by_path(file_path)
#             self._ide_search_init(view_editor.editor.get_buffer())
#             
#             # 分析标记
#             if self.cur_prj is not None:
#                 tags = self.cur_prj.query_tags_by_file(file_path)
#                 self.ide_refresh_file_tag_list(tags)
            self.ide_switch_page(file_path)

            result = self.RLT_OK

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel to open one file.")
            result = self.RLT_CANCEL
        
        self._set_status(ViewMenu.STATUS_FILE_OPEN)
        
        return result

    def ide_close_file(self, widget):
        '''
        如果打开了文件，
            如果文件已经修改过，保存当前的文件。
            关闭当前的文件。
            清除当前的Buffer。
        \return RLT_XXX
        '''
        print("ide close file.")
        
        ide_editor = self.multiEditors.get_current_ide_editor()
        if ide_editor is None or ide_editor.ide_file is None:
            print('No file is being opened')
            return self.RLT_OK
        
        needSave = False
        
        # 根据是否被修改了，询问是否需要保存。
        if ide_editor.editor.get_buffer().get_modified():
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION, \
                                       Gtk.ButtonsType.YES_NO, "文件已经被改变，是否保存？")
            response = dialog.run()
            dialog.reset_state()
            if response == Gtk.ResponseType.YES:
                needSave = True

        # 需要保存，就保存，如果不需要，就直接关闭。
        if needSave:
            result = self.ide_save_file(widget)
            if result != self.RLT_OK:
                return result
        
        # 关闭文件
        self.multiEditors.close_editor(self.multiEditors.get_current_abs_file_path())
        
        self._set_status(ViewMenu.STATUS_FILE_NONE)
        
        return self.RLT_OK
        
    def ide_save_file(self, widget):
        '''
        如果当前文件已经打开，并且已经修改了，就保存文件。
        '''
        
        print('ide save file')
        
        ide_editor = self.multiEditors.get_current_ide_editor()
        if ide_editor is None:
            print('No file is being opened.')
            return self.RLT_OK
        
        src_buffer = ide_editor.editor.get_buffer()
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
         
        dialog.reset_state()
        
    def ide_edit_redo(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return
        
        src_buffer = ve_editor.editor.get_buffer()
        src_buffer.redo()
    
    def ide_edit_undo(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return
        
        src_buffer = ve_editor.editor.get_buffer()
        src_buffer.undo()
        
    def ide_edit_cut(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return
        
        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = ve_editor.editor.get_clipboard(atom)
        ve_editor.editor.get_buffer().cut_clipboard(clipboard, True)
        
    def ide_edit_copy(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return
        
        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = ve_editor.editor.get_clipboard(atom)
        ve_editor.editor.get_buffer().copy_clipboard(clipboard)
        
    def ide_edit_paste(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return
        
        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = ve_editor.editor.get_clipboard(atom)
        ve_editor.editor.get_buffer().paste_clipboard(clipboard, None, True)
    
    def ide_edit_select_all(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return
        
        src_buffer = ve_editor.editor.get_buffer()
        src_buffer.select_range(src_buffer.get_start_iter(), src_buffer.get_end_iter())
        
    def ide_switch_page(self, abs_file_path):
        '''
        abs_file_path string 切换到的文件名字
        '''
        
        self.multiEditors.show_editor(abs_file_path)
        
        view_editor = self.multiEditors.get_editor_by_path(abs_file_path)
        self._ide_search_init(view_editor.editor.get_buffer())
            
        # 分析标记
        if self.cur_prj is not None:
            tags = self.cur_prj.query_tags_by_file(abs_file_path)
            self.ide_refresh_file_tag_list(tags)
            
        # 显示文件的路径。
        self.ide_set_title(abs_file_path)
        
        # 在文件树那里同步
        self.history_list.show_file(abs_file_path)
    
    ###################################
    ## 更加底层的功能
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
        
        buf = view_editor.editor.get_buffer()
         
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
        
        self._ide_search_text(view_editor.editor.get_buffer(), search_text)
        
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

        self._ide_search_text_next(view_editor.editor.get_buffer(), search_text)
        
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
        completion = editor.props.completion
        
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
