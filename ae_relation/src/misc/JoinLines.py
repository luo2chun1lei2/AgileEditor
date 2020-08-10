#-*- coding:utf-8 -*-

class JoinLines():
    # 合并多行
    def __init__(self):
        # 最新的一行命令。
        self.is_in_join = False
        self.cur_cmd = ""
        
    def in_join(self):
        return self.is_in_join
    
    def join(self, line_no, line):
        # @return None，合并了。other:合并后的行。
        if len(line) > 0 and line[-1] == '\\':
            self.cur_cmd += line[:-1]
            self.is_in_join = True
            return None
        
        tmp = self.cur_cmd + line
        
        #print "||>%s" % tmp
        
        self.cur_cmd = ""
        self.is_in_join = False
        
        return tmp