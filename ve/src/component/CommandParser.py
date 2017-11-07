# -*- coding:utf-8 -*-
'''
分析输入的命令。
'''
import getopt, logging
from framework.FwComponent import FwComponent

class CommandParser(FwComponent):
    def __init__(self):
        pass

    def onRegistered(self, manager):
        info = {'name':'command.parse', 'help':'parse the command options, and return result.'}
        manager.registerService(info, self)

        info = {'name':'command.help', 'help':'show command help infomation to console.'}
        manager.registerService(info, self)

        return True

    def onRequested(self, manager, serviceName, params):
        if serviceName == "command.parse":
            logging.debug("parse command")
            argv = params['argv']
            if argv is None:
                logging.error("Need command arguments.")
                return (False, None)
            return self._parseArgv(argv)

        elif serviceName == "command.help":
            return self._commandHelp()

        else:
            return (False, None)

    def _commandHelp(self):
        ''' 显示命令行的帮助信息。
        '''
        print 've usage:'
        print '-h, --help: print help message.'
        print '-p, --project <project name>: open the project. '
        print '-z: ve will find the corresponding project by current path.'
        print '-f, --file <file path>: open the file.'
        return (True, None)

    def _parseArgv(self, argv):
        want_open_file = None  # 想要立即打开的文件名字
        want_open_project_name = None  # 想要立即打开的项目名字
        want_lazy = False  # 想根据当前路径找到项目

        # parse the argv
        try:
            opts, args = getopt.getopt(argv[1:], 'hzp:f:', ['project=', 'file='])
        except getopt.GetoptError, err:
            print str(err)
            return (False, None)

        for o, a in opts:
            if o in ('-h', '--help'):
                '显示帮助信息'
                # 不调用 self._commandHelp()，让外部以为是错误，不再继续运行。
                return (False, None)
            elif o in ('-f', '--file'):
                want_open_file = a
            elif o in ('-z'):
                want_lazy = True
            elif o in ('-p', '--project'):
                want_open_project_name = a
            else:
                print 'unknown arguments.'
                return (False, None)

        info = {"want_open_file": want_open_file,
                "want_open_project_name": want_open_project_name,
                "want_lazy": want_lazy}
        return (True, info)
