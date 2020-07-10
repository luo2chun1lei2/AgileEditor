#!/bin/bash

# 普通的输入，包含
# 1. 命令：用于建立mvc
# 2. 输入信息：用于建立 model内的数据关系
# 普通输出，包含
# 1. 当前系统状态
# 2. 当前model的数据关系

# DISCUSS:
# 输入可以是命令行，
# 也可以是 interview 时的命令行
# 或者是写在脚本中

SCRIPT_HOME=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
AE_RELATION_HOME=$(cd "${SCRIPT_HOME}/.." && pwd)

# 建立一个基本的mvc，然后名字是 test，其他都是缺省的
ae_rlt "test" create
# 在test中建立基本的数据关系。
ae_rlt "test" element --name=123
# 在 test 中执行脚本，是为了建立基本的数据关系
ae_rlt "test" execute --script=${SCRIPT_HOME}/basic.txt
