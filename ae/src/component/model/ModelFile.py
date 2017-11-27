#-*- coding:utf-8 -*-

# 每个被打开的文件。
# 1, 可以读取文件内容。

import os.path, logging

class ModelFile(object):
    # 代表一个被打开的文件。
    # file_path:路径，如果是None，证明是新建的文件。
    # file_obj:文件对象(用open函数打开的句柄)。
    # file_search_key:每个文件的检索关键字，如果没有就设置成NIL。
    # 文件状态必须是打开或者创建后，然后进行读写操作，再关闭。
    
    def __init__(self):
        super(ModelFile, self).__init__()
        
        self.file_obj = None
        self.file_path = None
        self.file_search_key = None
        self.file_search_case_sensitive = True
        self.file_search_is_word = False
    
    def open_file(self, file_path):
        # 打开指定的文件。
        # file_path:string:文件的路径（绝对）
        # return:文件的file_obj.
        
        logging.debug('Open file:%s' % file_path)
        
        if(self.file_obj != None):
            logging.error('File(%s) has been opened.' % self.file_path)
            return None
        
        if os.path.exists(file_path):
            self.file_obj = open(file_path, 'r+')
        else:
            self.file_obj = open(file_path, 'w+')
        
        self.file_path = file_path
        
        return self.file_obj
    
    def read_file(self, src_buffer):
        # 读取文件内容。
        # buffer: GtkSource.Buffer: 画面空间的buffer
        # return: Nothing
        
        if self.file_obj == None:
            logging.error('File is NOT opened.')
            return
        
        # 无效undo动作管理器。
        src_buffer.begin_not_undoable_action()
        
        # 将文件中的数据放入Buffer中。
        # TODO: 对于大数据文件怎么办？
        src_buffer.delete(src_buffer.get_start_iter(), src_buffer.get_end_iter())
        
        # 读取的每行放入到buffer中。
        for line in self.file_obj:
            #print("" + line)
            src_buffer.insert(src_buffer.get_end_iter() ,line)
        
        # 开启undo动作。
        src_buffer.end_not_undoable_action()
            
    def save_file(self, src_buffer):
        # 保存文件
        # src_buffer:GtkSource.Buffer:画面编辑器的Buffer
        # return: Nothing
        
        if self.file_obj == None:
            logging.error('File is Not opened.')
            return
            
        text = src_buffer.get_text(src_buffer.get_start_iter(), src_buffer.get_end_iter(), False)

        # 删除原来的数据，然后写入新的数据
        self.file_obj.truncate(0)
        self.file_obj.seek(0, 0)
        self.file_obj.write(text)
        self.file_obj.flush()
    
    def close_file(self):
        # 关闭此文件
        
        if self.file_obj is None:
            return
        
        self.file_obj.close()
        self.file_obj = None
        self.file_path = None
