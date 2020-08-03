#-*- coding:utf-8 -*-

# Parser模块：
# 1. 解析传入的命令，变成标准的命令CommandPackage

class Parser(object):
    def __init__(self):
        super(Parser, self).__init__()
        
    def parse(self, input):
        # 对input进行分析
        # TODO: 目前这个接口无法统一参数！
        # @param input any type
        # @return CommandPackage[]
        
        return None

    def show_help(self):
        assert False