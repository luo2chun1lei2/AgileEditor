# -*- coding:utf-8 -*-
''' 【不是组件】一个Tag的信息。
以后作为所有检索结果、代码跳转的核心数据对象。
'''

class ModelTag(object):
    ''' 一个Tag的信息。
    tag_name:string:tag的名字
    tag_file_path:string:绝对文件路径
    tag_line_no:int:对应代码的行数
    tag_content:string:所在行的内容（不一定存在）
    tag_type:string:类型，可以通过ctags --list-kinds 来显示。
    tag_scope:string:tag所在的类，和上面的没有关系。
    '''

    def __init__(self, name,
                 file_path=None, line_no=None, content=None,
                 tag_type=None, tag_scope=None):
        super(ModelTag, self).__init__()
        self.tag_name = name
        self.tag_file_path = file_path
        self.tag_line_no = line_no
        self.tag_content = content
        self.tag_type = tag_type
        self.tag_scope = tag_scope
