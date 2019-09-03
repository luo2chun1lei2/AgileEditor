# -*- coding:utf-8 -*-

from CodernityDB.database import Database
 
def test_db():
    db = Database('/tmp/tut2')
    db.open()
     
    # insert one key:value into db.
    insertDict = {'x': 1}
    print db.insert(insertDict)
