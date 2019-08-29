# -*- coding:utf-8 -*-

from CodernityDB.database import Database
 
def test_db():
    db = Database('/tmp/tut1')
    db.create()
     
    insertDict = {'x': 1}
    print db.insert(insertDict)
