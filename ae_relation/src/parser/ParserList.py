#-*- coding:utf-8 -*-

# In this class keep a list of parsers.
# When parsing, use parser one by one.
# If parsing is finished, then return.

from parser.Parser import *
from misc import *

class ParserList(Parser):
    # Parser的列表，一个一个执行。

    def __init__(self, model,  *parsers):
        # @param model Model 在传入前，需要初始化好model。
        super(ParserList, self).__init__()
        self.parsers = parsers
        
        self.model = model
        
    def add_parser(self, parser):
        self.parsers.add(parser)
    
    def parse(self, line_no, line):
        # @return Return
        for p in self.parsers:
            rlt = p.parse(line_no, line)
            if rlt != None:
                logging.debug("Parser(%s) cannot parse this command:%s" % (type(p), line))
                return rlt
            
            # None时，继续下一个parser。

    def show_help(self):
        for p in self.parsers:
            p.show_help()
