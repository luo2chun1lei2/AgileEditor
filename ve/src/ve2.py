#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
2.0版本的ve入口。
'''

import sys, logging
from framework.FwManager import FwManager

def main(argv):
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')

    mng = FwManager.instance(argv)
    mng.run()

if __name__ == '__main__':
    # 主入口
    main(sys.argv)
