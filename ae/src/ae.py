#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
0.3版本的ae入口。
'''

import sys, logging

def init_components(manager):
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
    manager.register("ae_main", AeMain.get_instance())
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
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')

    from framework.FwManager import FwManager
    mng = FwManager.instance()
    init_components(mng)
    mng.run(argv)

if __name__ == '__main__':
    # 主入口
    main(sys.argv)