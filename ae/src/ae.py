#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
ae入口。
'''

import sys, logging

''' 提供的服务，组件并不是问题所在，服务才是。
    这里服务应该尽量隐藏组件内部实现的特点，留下通用、完整的服务接口，方便以后改为其他技术实现的组件。
    还需要：【用clang替换global需要很多的修改，这里放在最后】
    【所有的组件在初始化时，最好不要依赖其他的组件，比如menu，应该可以独立的初始化，这样，就从设计上避免了初始化顺序问题，但是顺序问题还是要讨论的】
    【还需要探讨可以实现多个同类型组件的实例，供不同的用途的问题】
    【editor切换时，文件内检索和跳转有冲突：
    1，search_entry输入时，必须根据输入而检索内容。
    2，当切换编辑文件时，还需要还原原来检索的情况。
    3，并且对应的检索内容需要修改，必然会发生search_entry的输入事件，如果内容相同，则不会发生事件。】

    # 辅助用的对话框(OK)。
    dialog.about/dialog.common.one_entry/dialog.common.two_entry/dialog.project.new
    dialog.project.open/dialog.project.change/dialog.project.setting
    dialog.msg.xxx 通用消息和问题类对话框。
    
    util.word_complete.get_provider

    # 应用程序级别的服务，模型是一个app，需要分析启动和设置，以及显示主画面。
    app.run/app.view.show/app.select_project [需要整理，选择一个项目成了画面的入口？][app是否综合为start/run/quit三个步骤?]
    app.command.parse/app.command.help
    
    # 数据模型，主要是内部数据的实例建立和永久保存等相关。
    model.jump_history.push/model.jump_history.pop [配合go_back_tag，修改成可以前进和后退的方式，以及显示history记录]
    model.workshop.getopt [是否考虑将下面的project的功能，放在workshop中，如果主要的工作都是workshop做的]
    model.project.new/model.project.delete/model.project.change [少了顺序的修改 move up/down][少了open，cur_prj应该放在workshop中]
    
    # 画面类型的组件，都应该有 get_view 获得组件中的view。
    view.menu.add/view.menu.set_and_jump_to_search_textbox[这个需要整理！]/view.menu.set_search_option
    [菜单还是不够美观][也不能独立的添加toolbar上面的按钮] [菜单无法根据当前状态来改变自己的status]
    
    view.main.get_window : get the main window.
    view.main.close_files : close all opened files.  [ -> 没有实现]
    view.main.get_current_project : get current project.    [-> model.workshop]
    view.main.set_current_project : set current project.    [-> model.workshop]
    view.main.get_current_workshop : get current workshop.  [-> model.workshop]
    view.main.close_current_project : close the current project.
    view.main.set_title : set title of window.
    view.main.set_status [set_status根本就没有实现]
    
    view.fstree.get_view/view.fstree.focus_file/view.fstree.set_dir [fstree实现太复杂，而且有太多bug，需要修改]
    
    view.file_taglist.get_view/view.file_taglist.show_taglist
    [点击事件变成event]
    
    view.search_taglist.get_view/view.search_taglist.show_taglist
    
    view.multi_editors.get_view/view.multi_editors.open_editor/view.multi_editors.close_editor
    [下面获取属性的服务太多，应该写成一个，减少复杂性]
    view.multi_editors.get_editor_by_path : get current editor by path.
    view.multi_editors.get_current_editor : get current editor.
    view.multi_editors.get_current_ide_editor : get current editor.
    view.multi_editors.get_current_abs_file_path : get absolutive path of current file.
    view.multi_editors.get_current_ide_file : show model of current file.
    [修改editor的属性的太多了，变成".set_opt",然后具体的内容和值放在params中]
    view.multi_editors.change_editor_style : change the style scheme of editors.
    view.multi_editors.change_editor_font : change the font of editors.
    
    view.terminal.get_view/view.terminal.init  [init可以合并到get_view中]
    view.bookmarks.get_view/view.bookmarks.add_bookmark/view.bookmarks.remove_bookmark [bookmark是否随着修改，也不改变所在的行？]
    
    控制类的服务，它实现的是UI，里面会操作Model和View，也不仅限于此。
    - 和文本编辑相关的操作
    ctrl.edit.redo/ctrl.edit.undo 【redo和undo好像总是运行不正常，如果修改了多个文件后，按下undo时】
    ctrl.edit.cut/ctrl.edit.copy/ctrl.edit.paste
    ctrl.edit.comment/ctrl.edit.uncomment
    ctrl.edit.replace/ctrl.edit.delete_line/ctrl.edit.select_all [select all是否应该放到 ctrl.search 中?]
    - 和检索相关的操作，虽然也是和文件相关的，但是因为服务比较多，所以单独列出来。
      检索分成三种技术：用global、grep和在editor's buffer 中，需要做出统一的接口，无论到底用哪种技术检索的。
      【另外，grep、editor本身的检索技术基本成熟了，但是基于source的代码分析（比如global/clang)等还在不断的发展，
      所以应该建立一个source search的组件，实现底层的source navigator，方便以后替换。】
    ctrl.search.init [不如变成设置检索的参数]
    ctrl.search.goto_line/ctrl.search.jump_to [goto_line 和 jump_to 是否重复了？]
    ctrl.search.focus_on_entry
    ctrl.search.find_text : begin to find text.
    ctrl.search.find_next : find the next matched word.
    ctrl.search.find_prev : find the previous matched word.
    ctrl.search.find_in_files : find the matched word in files. [应该是在project中！]
    ctrl.search.find_in_files_again : find the matched word in files again.
    ctrl.search.find_path
    ctrl.search.find_definition/ctrl.search.find_definition_need_input
    ctrl.search.find_reference/ctrl.search.find_reference_need_input
    ctrl.search.go_back_tag [配合jump_history，实现更强的跳转功能]
    ctrl.search.update_tags
    ctrl.search.show_bookmark/ctrl.search.make_bookmark [这部分的服务和 view.bookmark.add_bookmark的主导关系需要颠倒一下。]
    - 和workshop、project相关的操作。
    ctrl.workshop.preference : set preference of workshop.
    ctrl.workshop.new_project/ctrl.workshop.open_project/ctrl.workshop.close_project/ctrl.workshop.app_quit
    [缺少删除操作, app_quit怎么在这里，应该在app层吧？]
    - 和文件相关的操作，和上面的ws、prj操作从层次上来说，并无太多不同。
    ctrl.file.new /ctrl.file.open/ctrl.file.close/ctrl.file.save/ctrl.file.save_as
    [少一个rename，再加一个统计（大小、修改时间等）] [缺少关闭所有文件，或者其他文件等操作]
'''

def load_components(manager):
    ''' 建立最开始的组件，然后注册。
    '''
    # 注册已知的组件工厂。
    # TODO 以后修改成从固定文件夹等搜索组件，然后加载。
    from component.AppProcess import AppProcess
    from component.AppView import AppView
    from component.AppArgs import AppArgs
    from component.dialog.ViewDailogAbout import ViewDialogAbout
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
    from component.control.CtrlHelp import CtrlHelp
    from component.dialog.ViewDialogMsg import ViewDialogMsg
    from component.dialog.ViewDialogInfo import ViewDialogInfo
    from component.view.ViewPogress import ViewProgress
    from component.model.ModelTagsGlobal import ModelTagsGlobal

    manager.register("app_process", AppProcess())
    manager.register("command_parser", AppArgs())
    manager.register("app_view", AppView())
    manager.register("ae_main", AeMain())
    manager.register("dialog_about", ViewDialogAbout())
    manager.register("dialog_common", ViewDialogCommon())
    manager.register("dialog_project", ViewDialogProject())
    manager.register("dialog_project_setting", ViewDialogWorkshopSetting())
    manager.register("dialog_msg", ViewDialogMsg())
    manager.register("dialog_info", ViewDialogInfo())
    manager.register("word_complete", UtilWordComplete())
    manager.register("fs_treeview", ViewFsTree())
    manager.register("file_taglist", ViewFileTagList())
    manager.register("search_taglist", ViewSearchTagList())
    manager.register("multiple_editors", ViewMultiEditors())
    manager.register("terminal", ViewTerminal())
    manager.register("bookmarks", ViewBookmarks())
    manager.register("jump_history", ModelJumpHistory())
    manager.register("ctrl_edit", CtrlEdit())
    manager.register("ctrl_search", CtrlSearch())
    manager.register("ctrl_workshop", CtrlWorkshop())
    manager.register("ctrl_file", CtrlFile())
    manager.register("ctrl_help", CtrlHelp())
    manager.register("view_progress", ViewProgress())
    manager.register("model_tags_global", ModelTagsGlobal())



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
