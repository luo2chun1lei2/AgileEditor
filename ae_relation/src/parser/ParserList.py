#-*- coding:utf-8 -*-

# In this class keep a list of parsers.
# When parsing, use parser one by one.
# If parsing is finished, then return.

import logging

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
        logging.debug("Parse \"%d:%s\"" % (line_no, line))
        # @return Return
        for p in self.parsers:
            logging.debug("parser=%s"  % type(p))
            rlt = p.parse(line_no, line)
            if rlt != None:
                return rlt
            else:
                # None时，继续下一个parser。
                logging.debug("  Cannot parse this command:%s" % (line))

    def show_help(self):
        for p in self.parsers:
            p.show_help()
