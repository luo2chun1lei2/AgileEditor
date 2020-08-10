# -*- coding:utf-8 -*-
'''
Parser
输入的命令的分析,或者某些代码的分析，总之来自一切外部的数据转化为Process的输入。
Process可以是Model或者Container。
'''

from .CommandPackage import *

from .Parser import *
from .ParserInteractiveCommand import *
from parser.ParserUML import *
from .ParserAppOption import *
from .ParserBasic import *
from .ParserList import *