# -*- coding:utf-8 -*-
'''
控制和文件相关的部分。
'''
import logging, shutil
from gi.repository import Gdk, GLib, Gtk, GtkSource

from framework.FwComponent import FwComponent
from framework.FwManager import FwManager

from component.model.ModelTask import ModelTask
from component.model.ModelWorkshop import ModelWorkshop
from component.util.UtilEditor import UtilEditor
from component.util.UtilDialog import UtilDialog
from component.view.ViewWindow import ViewWindow
from component.model.ModelProject import ModelProject
from component.view.ViewMenu import ViewMenu

class CtrlFile(FwComponent):
    def __init__(self):
        super(FwComponent, self).__init__()

    # override component
    def onRegistered(self, manager):
        info = [{'name':'ctrl.file.new', 'help':'create new file.'},
                {'name':'ctrl.file.open', 'help':'open one file.'},
                {'name':'ctrl.file.close', 'help':'close current opened file.'},
                {'name':'ctrl.file.save', 'help':'save current opened file.'},
                {'name':'ctrl.file.save_as', 'help':'save current opened file as another name.'}
                ]
        manager.registerService(info, self)

        # register listening event.
        manager.register_event_listener('view.multi_editors.switch_page', self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "ctrl.file.new":
            rlt = self._new_file()
            return (True, {'result': rlt})
        elif serviceName == 'ctrl.file.open':
            if 'abs_file_path' in params:
                rlt = self._open_file(params['abs_file_path'])
            else:
                rlt = self._open_file()
            return (True, {'result': rlt})
        elif serviceName == 'ctrl.file.close':
            rlt = self._close_file()
            if rlt == ViewWindow.RLT_OK:
                self._new_file()
            return (True, {'result': rlt})
        elif serviceName == 'ctrl.file.save':
            rlt = self._save_file()
            return (True, {'result': rlt})
        elif serviceName == 'ctrl.file.save_as':
            rlt = self._save_as_file()
            return (True, {'result': rlt})
        else:
            return (False, None)

    # override FwListener
    def on_listened(self, event_name, params):
        if event_name == 'view.multi_editors.switch_page':
            self._switch_page(params['abs_file_path'])
            return True
        else:
            return False

    # override component
    def onSetup(self, manager):
        params = {'menu_name':'FileMenu',
                  'menu_item_name':'FileNew',
                  'title':'Create a File',
                  'accel':"<control>N",
                  'stock_id':Gtk.STOCK_NEW,
                  'service_name':'ctrl.file.new',
                  'in_toolbar':True}
        manager.requestService("view.menu.add", params)

        params = {'menu_name':'FileMenu',
                  'menu_item_name':'FileOpen',
                  'title':'Open a file',
                  'accel':"<control>O",
                  'stock_id':Gtk.STOCK_OPEN,
                  'service_name':'ctrl.file.open',
                  'in_toolbar':True}
        manager.requestService("view.menu.add", params)

        params = {'menu_name':'FileMenu',
                  'menu_item_name':'FileClose',
                  'title':'Close current file',
                  'accel':"<control>W",
                  'stock_id':Gtk.STOCK_CLOSE,
                  'service_name':'ctrl.file.close',
                  'in_toolbar':True}
        manager.requestService("view.menu.add", params)

        params = {'menu_name':'FileMenu',
                  'menu_item_name':'FileSave',
                  'title':"Save current file",
                  'accel':"<control>S",
                  'stock_id':Gtk.STOCK_SAVE,
                  'service_name':'ctrl.file.save',
                  'in_toolbar':True}
        manager.requestService("view.menu.add", params)

        params = {'menu_name':'FileMenu',
                  'menu_item_name':'FileSaveAs',
                  'title':"Save current file as ...",
                  'accel':"",
                  'stock_id':Gtk.STOCK_SAVE_AS,
                  'service_name':'ctrl.file.save_as',
                  'in_toolbar':True}
        manager.requestService("view.menu.add", params)

        return True

    def _new_file(self):
        ''' 建立一个新文件。 TODO 原来就是什么都没有实现。
        '''
        pass

    def _save_file(self):
        ''' 如果当前文件已经打开，并且已经修改了，就保存文件。
        '''

        logging.debug('start to save file.')

        ide_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
        if ide_editor is None:
            logging.debug('No file is being opened.')
            return ViewWindow.RLT_OK

        src_buffer = ide_editor.editor.get_buffer()
        if src_buffer.get_modified():
            if ide_editor.ide_file.file_path is None:
                dialog = Gtk.FileChooserDialog("请选择一个文件", None,
                           Gtk.FileChooserAction.SAVE ,
                           (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                Gtk.STOCK_OK, Gtk.ResponseType.OK))

                response = dialog.run()
                file_path = dialog.get_filename()
                dialog.destroy()

                if response == Gtk.ResponseType.OK:
                    logging.debug("File selected: " + file_path)

                    # 打开一个空的文件，或者里面已经有内容了。
                    ide_editor.ide_file.open_file(file_path)
                    UtilEditor.set_src_language(src_buffer, file_path)

                elif response == Gtk.ResponseType.CANCEL:
                    logging.debug("Cancel to save one file.")
                    return ViewWindow.RLT_CANCEL

            # 将内容保存到文件中。
            ide_editor.ide_file.save_file(UtilEditor.get_editor_buffer())
            src_buffer.set_modified(False)
            logging.debug('ide save file to disk file.')

            # 重新整理TAGS
            cur_prj = FwManager.requestOneSth('project', 'view.main.get_current_project')
            cur_prj.prepare()

            # 右边的TAG更新
            self._query_tags_by_file_and_refresh(ide_editor.ide_file.file_path)

        FwManager.instance().requestService('view.main.set_status', {'status':ViewMenu.STATUS_FILE_OPEN})

        return ViewWindow.RLT_OK

    def _refresh_file_tag_list(self, tags):
        # 根据Tag的列表，更新文件对应的Tag列表
        # tags:[IdeOneTag]:Tag列表。
        FwManager.instance().requestService('view.file_taglist.show_taglist', {'taglist':tags})

    def _query_tags_by_file_and_refresh(self, abs_file_path):
        cur_prj = FwManager.requestOneSth('project', 'view.main.get_current_project')
        ModelTask.execute(self._refresh_file_tag_list,
                          cur_prj.query_ctags_of_file, abs_file_path)

    def _close_file(self):
        '''打开了文件，如果文件已经修改过，保存当前的文件。
            关闭当前的文件。清除当前的Buffer。
        @return RLT_XXX
        '''
        logging.debug("start to close file.")

        ide_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
        if ide_editor is None or ide_editor.ide_file is None:
            logging.debug('No file is being opened')
            return ViewWindow.RLT_OK

        needSave = False

        # 根据是否被修改了，询问是否需要保存。
        if ide_editor.editor.get_buffer().get_modified():
            dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.QUESTION, \
                                       Gtk.ButtonsType.YES_NO, "文件已经被改变，是否保存？")
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                needSave = True

        # 需要保存，就保存，如果不需要，就直接关闭。
        if needSave:
            result = self._save_file()
            if result != ViewWindow.RLT_OK:
                return result

        # 关闭文件
        abs_file_path = FwManager.requestOneSth('abs_file_path', 'view.multi_editors.get_current_abs_file_path')
        FwManager.instance().requestService('view.multi_editors.close_editor', {'abs_file_path': abs_file_path})

        # 关闭文件的tag列表。
        FwManager.instance().requestService('view.file_taglist.show_taglist', {'taglist': []})

        FwManager.instance().requestService('view.main.set_status', {'status':ViewMenu.STATUS_FILE_NONE})

        return ViewWindow.RLT_OK

    def _save_as_file(self):
        '''
        显示对话框，选择另存为的文件名字。
        然后关闭当前文件，
        创建新的Ide文件，打开这个文件，并保存。
        '''
        logging.debug("ide save as other file.")

        ide_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
        old_file_path = FwManager.requestOneSth('abs_file_path', 'view.multi_editors.get_current_abs_file_path')

        if ide_editor.ide_file == None:
            logging.debug('No file is being opened')
            return ViewWindow.RLT_OK

        # 如果是新文件，则按照Save的逻辑进行
        src_buffer = UtilEditor.get_editor_buffer()
        if src_buffer.get_modified():
            if ide_editor.ide_file.file_path is None:
                return self._save_file()

        # 如果是已经打开的文件，就将当前文件保存成新文件后，关闭旧的，打开新的。
        # 设定新的文件路径
        dialog = Gtk.FileChooserDialog("请选择一个文件", None, \
                                               Gtk.FileChooserAction.SAVE , \
                                               (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, \
                                                Gtk.STOCK_OK, Gtk.ResponseType.OK))

        response = dialog.run()
        file_path = dialog.get_filename()
        dialog.destroy()

        if response == Gtk.ResponseType.CANCEL:
            logging.debug("Cancel to save as one file.")
            return ViewWindow.RLT_CANCEL

        logging.debug("File selected: " + file_path)

        # 将当前文件保存成新文件
        shutil.copy(old_file_path, file_path)

        # 关闭原来的文件。
        FwManager.instance().requestService('view.multi_editors.close_editor', {'abs_file_path': old_file_path})

        # 打开指定的文件，并保存
        FwManager.instance().requestService('view.multi_editors.open_editor', {'abs_file_path': file_path})

        # 切换当前的状态
        FwManager.instance().requestService('view.main.set_status', {'status':ViewMenu.STATUS_FILE_OPEN})

        return ViewWindow.RLT_OK

    def _open_file(self, path=None):
        ''' 如果已经打开文件，变为当前文件。如果路径是空，就显示“挑选”文件。然后打开此文件。
        @param path:string:绝对路径。
        '''
        result = ViewWindow.RLT_CANCEL

        if(path is None):
            dialog = Gtk.FileChooserDialog("请选择一个文件", None,
                    Gtk.FileChooserAction.OPEN,
                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                     Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

            UtilDialog.add_filters(dialog)

            response = dialog.run()

            file_path = dialog.get_filename()
            dialog.destroy()
        else:
            response = Gtk.ResponseType.OK
            file_path = path

        if response == Gtk.ResponseType.OK:
            logging.debug("File selected: %s " % file_path)
            self._open_page(file_path)

            result = ViewWindow.RLT_OK

        elif response == Gtk.ResponseType.CANCEL:
            logging.debug("Cancel to open one file.")
            result = ViewWindow.RLT_CANCEL

        FwManager.instance().requestService('view.main.set_status', {'status':ViewMenu.STATUS_FILE_OPEN})

        # 设定单词补全。
        cur_prj = FwManager.requestOneSth('project', 'view.main.get_current_project')
        UtilEditor.set_completion(cur_prj)

        return result

    def _open_page(self, abs_file_path):
        '''
        @param abs_file_path: string: 切换到的文件名字
        '''
        FwManager.instance().requestService('view.multi_editors.open_editor', {'abs_file_path': abs_file_path})

        view_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_editor_by_path', {'abs_file_path': abs_file_path})
        FwManager.instance().requestService('ctrl.search.init', {'text_buffer':view_editor.editor.get_buffer()})

        # 分析标记
        cur_prj = FwManager.requestOneSth('project', 'view.main.get_current_project')
        if cur_prj is not None:
            # tags = self.cur_prj.query_tags_by_file(abs_file_path)
            # self.ide_refresh_file_tag_list(tags)
            # 在switch page时，会引发switch事件，调用_switch_page，会重新查询tags。
            pass

        # 显示文件的路径。
        FwManager.instance().requestService('view.main.set_title', {'title':abs_file_path})

        # 在文件树那里同步
        FwManager.instance().requestService('view.fstree.focus_file', {'abs_file_path':abs_file_path})

    def _switch_page(self, abs_file_path):
        # abs_file_path string 切换到的文件名字
        FwManager.instance().requestService('view.multi_editors.open_editor', {'abs_file_path': abs_file_path})

        view_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_editor_by_path', {'abs_file_path': abs_file_path})
        mdl_file = view_editor.ide_file

        # 初始化检索。
        # - 检索会影响到位置，这里只有在函数结尾再加上定位了。
        FwManager.instance().requestService('ctrl.search.init', {'text_buffer':view_editor.editor.get_buffer()})
        FwManager.instance().requestService('view.menu.set_search_option',
                    {'search_text':mdl_file.file_search_key, 'case_sensitive':mdl_file.file_search_case_sensitive, 'is_word':mdl_file.file_search_is_word})

        # 分析标记
        cur_prj = FwManager.requestOneSth('project', 'view.main.get_current_project')
        if cur_prj is not None:
            self._query_tags_by_file_and_refresh(abs_file_path)

        # 显示文件的路径。
        FwManager.instance().requestService('view.main.set_title', {'title':abs_file_path})

        # 在文件树那里同步
        FwManager.instance().requestService('view.fstree.focus_file', {'abs_file_path':abs_file_path})
