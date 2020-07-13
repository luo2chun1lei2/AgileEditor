#!/bin/bash

# 最简单的测试。

SCRIPT_HOME=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
AE_RELATION_HOME=$(cd "${SCRIPT_HOME}/.." && pwd)

# 建立一个基本的mvc，然后名字是 test，其他都是缺省的
ae_rlt --model test --script=${SCRIPT_HOME}/sequence.txt
