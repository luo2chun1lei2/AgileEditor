# -*- coding:utf-8 -*-

# 最基本的 Element 和 Relation

import os, sys, logging, getopt, shutil, traceback

from misc import *

from model.Relation import *
from model.Element import *
from model.Model import *

class ModelBasic(Model):
    def __init__(self):
        super(ModelBasic, self).__init__()