#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
0.3版本的ae入口。
'''

import sys, logging

''' 提供的服务，组件并不是问题所在，服务才是。

    # 应用程序级别的service。
    app.run/app.view.show/app.select_project[需要整理，选择一个项目成了画面的入口？]
    app.command.parse/app.command.help
    
    # 辅助用的对话框(OK)。
    # TODO 还是显示对话框没有parent，我已经取得了window？
    dialog.info/dialog.common.one_entry/dialog.common.two_entry/dialog.project.new
    dialog.project.open/dialog.project.change/dialog.project.setting
    
    # 模型这里比较少，多数放到了view.window中了。
    model.workshop.xxx/model.project.xxx/model.jump_history.push/model.jump_history.pop 
    model.workshop.getopt/model.project.new/model.project.delete/model.project.change
    
    util.word_complete.get_provider
    
    # 画面类型的组件，都应该有 get_view 获得组件中的中view。
    view.menu.add/view.menu.set_and_jump_to_search_textbox[这个需要整理！]/view.menu.set_search_option
    view.main.get_window : get the main window.
    view.main.close_files : close all opened files.
    view.main.get_current_project : get current project.  -> [model.workshop]
    view.main.set_current_project : set current project.  -> [model.workshop]
    view.main.get_current_workshop : get current workshop.  -> [model.workshop]
    view.main.close_current_project : close the current project.
    view.main.set_title : set title of window.
    view.main.set_status : set status of window.
    view.fstree.get_view : get the whole view.
    view.fstree.focus_file : set focus to the given file.
    view.fstree.set_dir : set file-tree path.
    view.file_taglist.get_view : get view of tag list.
    view.file_taglist.show_taglist : show tag list in view.
    view.search_taglist.get_view : get view of search taglist.
    view.search_taglist.show_taglist : show tag list in view.
    view.multi_editors.get_view : get view of multiple editors.
    view.multi_editors.show_taglist : show tag list in view.
    view.multi_editors.open_editor : open one editor.
    view.multi_editors.close_editor : close one editor.
    view.multi_editors.get_editor_by_path : get current editor by path.
    view.multi_editors.get_current_editor : get current editor.
    view.multi_editors.get_current_ide_editor : get current editor.
    view.multi_editors.get_current_abs_file_path : get absolutive path of current file.
    view.multi_editors.get_current_ide_file : show model of current file.
    view.multi_editors.change_editor_style : change the style scheme of editors.
    view.multi_editors.change_editor_font : change the font of editors.
    view.terminal.get_view : get view of ternimal.
    view.terminal.init : initialize the terminal.
    view.bookmarks.add_bookmark : add one bookmark by current pos.
    view.bookmarks.remove_bookmark : remove one bookmark by current pos.
    view.bookmarks.get_view : get view of bookmark.
    
    控制类的服务，不仅仅是根据数据更新view，而是需要协调UI的动作。
    ctrl.edit.redo : redo.
    ctrl.edit.undo : undo.
    ctrl.edit.cut : cut the selected text.
    ctrl.edit.copy : copy the selected text.
    ctrl.edit.paste : paste the text in clipboard.
    ctrl.edit.comment : make selected code to comment.
    ctrl.edit.uncomment : make selected code to uncomment.
    ctrl.edit.replace : replace the selected text by other text.
    ctrl.edit.delete_line : delete the line allocated by cursor.
    ctrl.edit.select_all : select all test in current edit file.
    ctrl.search.init : initialize the search context.
    ctrl.search.goto_line : goto the given line and focus on editor.
    ctrl.search.jump_to : Jump to ? line.
    ctrl.search.find : get the selected word and focus on search textbox.
    ctrl.search.find_text : begin to find text.
    ctrl.search.find_next : find the next matched word.
    ctrl.search.find_prev : find the previous matched word.
    ctrl.search.find_in_files : find the matched word in files.
    ctrl.search.find_in_files_again : find the matched word in files again.
    ctrl.search.find_path : find the match path.
    ctrl.search.find_definition_input_by_dialog : show dialog to get the symbol, and then find the definition.
    ctrl.search.find_definition : find the definition of symbol.
    ctrl.search.find_reference : find the reference of symbol.
    ctrl.search.go_back_tag : go back to the previous tag.
    ctrl.search.update_tags : go back to the previous tag.
    ctrl.search.show_bookmark : show a bookmark.
    ctrl.search.make_bookmark : make one bookmark by current position, and return bookmarks list
    ctrl.workshop.preference : set preference of workshop.
    ctrl.workshop.new_project : create a new project.
    ctrl.workshop.open_project : open one project.
    ctrl.workshop.close_project : close the current project.
    ctrl.workshop.app_quit : quit from app.
    ctrl.file.new : create new file.
    ctrl.file.open : open one file.
    ctrl.file.close : close current opened file.
    ctrl.file.save : save current opened file.
    ctrl.file.save_as : save current opened file as another name.
    
'''

def load_components(manager):
    ''' 建立最开始的组件，然后注册。
    '''
    # 注册已知的组件工厂。
    # TODO 以后修改成从固定文件夹等搜索组件，然后加载。
    from component.AppProcess import AppProcess
    from component.AppView import AppView
    from component.AppArgs import AppArgs
    from component.dialog.ViewDailogInfo import ViewDialogInfo
    from component.dialog.ViewDialogCommon import ViewDialogCommon
    from component.dialog.ViewDialogProject import ViewDialogProject
    from component.dialog.ViewDialogWorkshopSetting import ViewDialogWorkshopSetting
    from component.util.UtilWordComplete import UtilWordComplete
    from component.view.ViewFsTree import ViewFsTree
    from component.view.ViewFileTagList import ViewFileTagList
    from component.view.ViewSearchTagList import ViewSearchTagList
    from component.view.ViewTerminal import ViewTerminal
    from component.view.AeMain import AeMain
    from component.view.ViewMultiEditors import ViewMultiEditors
    from component.view.ViewBookmarks import ViewBookmarks
    from component.control.CtrlEdit import CtrlEdit
    from component.control.CtrlSearch import CtrlSearch
    from component.model.ModelJumpHistory import ModelJumpHistory
    from component.control.CtrlWorshop import CtrlWorkshop
    from component.control.CtrlFile import CtrlFile

    manager.register("app_process", AppProcess())
    manager.register("command_parser", AppArgs())
    manager.register("app_view", AppView())
    manager.register("ae_main", AeMain())
    manager.register("dialog_info", ViewDialogInfo())
    manager.register("dialog_common", ViewDialogCommon())
    manager.register("dialog_project", ViewDialogProject())
    manager.register("dialog_project_setting", ViewDialogWorkshopSetting())
    manager.register("word_complete", UtilWordComplete())
    manager.register("fs_treeview", ViewFsTree())
    manager.register("file_taglist", ViewFileTagList())
    manager.register("search_taglist", ViewSearchTagList())
    manager.register("multiple_editors", ViewMultiEditors())
    manager.register("terminal", ViewTerminal())
    manager.register("bookmarks", ViewBookmarks())
    manager.register("ctrl_edit", CtrlEdit())
    manager.register("ctrl_search", CtrlSearch())
    manager.register("jump_history", ModelJumpHistory())
    manager.register("ctrl_workshop", CtrlWorkshop())
    manager.register("ctrl_file", CtrlFile())

    # 这里用 manager.register 函数，在mng.run中，都需要调用 manager.load 函数。

def main(argv):
    logging.basicConfig(level=logging.INFO, 
                        format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')

    from framework.FwManager import FwManager
    mng = FwManager.instance()
    load_components(mng)
    mng.run(argv)

if __name__ == '__main__':
    # 主入口
    main(sys.argv)
