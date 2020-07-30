# -*- coding:utf-8 -*-

# 使用Prompt-toolkit输入文字。
# 1. 以行为基本单位。但并不是说，一行就一定处理结果。文本后面不包括"\n"。

from __future__ import unicode_literals

import logging, sys
from .Input import *

# 用于命令提示

reload(sys)
sys.setdefaultencoding('utf8')

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter 
    
# 在内部控制或者脚本可以执行的命令。
# TODO : 应该用当前Parser或者当前Control来提供
CMDLINE_CMD = ['help', 'app_quit', 'test',
                    'select', 'from', 'insert', 'update', 'delete', 'drop']
    
class InputPrompt(Input):
    # 从控制台获取输入。
    
    def __init__(self):
        super(InputPrompt, self).__init__()
        
        # 设定命令的提示符号。
        # TODO 提示的关键字，需要和下面的命令解析配套。
        self.word_completer = WordCompleter(CMDLINE_CMD, ignore_case=True)
        self.line_no = 0
        
    def read_line(self, wait=True):
        input_str = prompt('>', completer=self.word_completer,
              complete_while_typing=False)
        self.line_no = self.line_no + 1
        
        return self.line_no, input_str
        