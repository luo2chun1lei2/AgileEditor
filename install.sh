#!/bin/bash

PY_HOME=$(cd `dirname $0`; pwd)

cd ~
if [ ! -d bin ]; then
	mkdir bin
fi

cd bin

echo "python $PY_HOME/ae/src/ae.py \$* >/dev/null 2>&1 &" > ae
chmod a+x ae

echo "python $PY_HOME/ae_starter/src/main.py \$* >/dev/null 2>&1 &" > ae_starter
chmod a+x ae_starter

echo "python $PY_HOME/ae_executor/src/main.py \$* >/dev/null 2>&1 &" > ae_executor
chmod a+x ae_executor
