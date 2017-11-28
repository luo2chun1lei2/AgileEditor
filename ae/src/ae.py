#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
0.3版本的ae入口。
'''

import sys, logging

''' 提供的服务，组件并不是问题所在，服务才是。
    这里服务应该尽量隐藏组件内部实现的特点，留下通用、完整的服务接口，方便以后改为其他技术实现的组件。

    # 辅助用的对话框(OK)。
    # TODO 还是显示对话框没有parent，我已经取得了window？
    dialog.info/dialog.common.one_entry/dialog.common.two_entry/dialog.project.new
    dialog.project.open/dialog.project.change/dialog.project.setting
    [还有一堆通用的简单对话框（比如错误信息等），这里也应该变成统一的组件化]
    
    util.word_complete.get_provider [孤独的工具类，是否应该将dialog也归于util里面？]

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
    
    view.file_taglist.get_view/view.file_taglist.show_taglist [需要更加的高级clang，而不再使用global]
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
    ctrl.edit.redo/ctrl.edit.undo
    ctrl.edit.cut/ctrl.edit.copy/ctrl.edit.paste
    ctrl.edit.comment/ctrl.edit.uncomment
    ctrl.edit.replace/ctrl.edit.delete_line/ctrl.edit.select_all [select all是否应该放到 ctrl.search 中?]
    - 和检索相关的操作，虽然也是和文件相关的，但是因为服务比较多，所以单独列出来。
      检索分成三种技术：用global、grep和在editor's buffer 中，需要做出统一的接口，无论到底用哪种技术检索的。
      【另外，grep、editor本身的检索技术基本成熟了，但是基于source的代码分析（比如global/clang)等还在不断的发展，
      所以应该建立一个source search的组件，实现底层的source navigator，方便以后替换。】
    ctrl.search.init [不如变成设置检索的参数]
    ctrl.search.goto_line/ctrl.search.jump_to [goto_line 和 jump_to 是否重复了？]
    ctrl.search.find [实际上是为了跳转到search entry控件，这里服务和工作不符]
    ctrl.search.find_text : begin to find text.
    ctrl.search.find_next : find the next matched word.
    ctrl.search.find_prev : find the previous matched word.
    ctrl.search.find_in_files : find the matched word in files. [应该是在project中！]
    ctrl.search.find_in_files_again : find the matched word in files again.
    ctrl.search.find_path/ctrl.search.find_definition_input_by_dialog  [检索用的路径可以从多处获取，最好不要添加多余的命令和UI，避免用户迷惑]
    ctrl.search.find_definition : find the definition of symbol. [也需要有dialog的]
    ctrl.search.find_reference : find the reference of symbol. [也需要有dialog的]
    ctrl.search.go_back_tag [配合jump_history，实现更强的跳转功能]
    ctrl.search.update_tags
    ctrl.search.show_bookmark/ctrl.search.make_bookmark [缺少删除操作]
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
