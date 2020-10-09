#!/bin/bash

# 允许运行各种SCRIPT。

SCRIPT_HOME=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
AE_RELATION_HOME=$(cd "${SCRIPT_HOME}/.." && pwd)

#用命令传入的脚本名字来运行。
# TODO: 需要设定不同的processor，难道不能在script中自己标定吗？不然我怎么知道。
cd ${AE_RELATION_HOME}
ae_rlt --script=${SCRIPT_HOME}/$*
