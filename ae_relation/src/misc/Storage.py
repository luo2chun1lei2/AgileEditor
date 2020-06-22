# -*- coding:utf-8 -*-

u'''
利用 CodernityDB 保存当前的模型。
TODO: 目前还没有真正使用，是否大材小用？
'''

from CodernityDB.database import Database
 
def test_db():
    db = Database('/tmp/tut2')
    db.open()
     
    # insert one key:value into db.
    insertDict = {'x': 1}
    print db.insert(insertDict)
