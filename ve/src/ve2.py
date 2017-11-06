#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
2.0版本的ve入口。
- 能够做成组件的，尽量做成组件。
'''

import sys, logging

def main(argv):
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')

    from framework.FwManager import FwManager
    mng = FwManager.instance(argv)
    mng.run()

if __name__ == '__main__':
    # 主入口
    main(sys.argv)
