#!/bin/bash

# add all libraries needed by this project.
sudo apt-get install python-pyinotify ctags global
#sudo apt-get install python-bzrlib python-pyinotify python-keybinder ctags global
#sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0

sudo apt install libgirepository1.0-dev
# 如果用pyenv 导致pip采用了python3 的pip3，那么需要
# pyenv install 2.7.18
# export PYENV_VERSION=2.7.18
pip install PyGObject bzr
