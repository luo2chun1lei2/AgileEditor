# -*- coding:utf-8 -*-

# 操纵 Graphivz 工具。
# 机器必须安装Graphivz，也就必须有 dot 命令。

import os, sys, subprocess, logging

class Graphivz(object):

    def __init__(self):
        # 没有什么可以初始化的。
        super(Graphivz, self).__init__()

    def create_diagram(self, data_path, out_path):
        # @param data_path:string: data file path
        # @param out_path:string: output file path
        # @return True: ok, False: failed.
        
        logging.debug("open %s" % data_path)
        f = open(data_path)
        for l in f:
            logging.debug(l)
        f.close()
        
        command = "dot -Tsvg %s -o %s" % (data_path, out_path)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE) 
        out, err = p.communicate()
        
        if err is not None:
            print err
            return False

        # show diagram
        os.system('eog %s' % (out_path))
