#!/bin/bash

# 测试各种参数，针对命令行

SCRIPT_HOME=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
AE_RELATION_HOME=$(cd "${SCRIPT_HOME}/.." && pwd)

# 执行基本的脚本。
ae_rlt --execute ${SCRIPT_HOME}/basic.txt