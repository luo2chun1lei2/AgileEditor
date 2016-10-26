#!/bin/bash

PY_HOME=$(cd `dirname $0`; pwd)

cd ~
if [ ! -d bin ]; then
	mkdir bin
fi

cd bin

if [ -f ve ]; then
	rm ve
fi
echo "python $PY_HOME/ve/src/ve.py \$*" > ve
chmod a+x ve

echo "You should add ~/bin in PATH."
