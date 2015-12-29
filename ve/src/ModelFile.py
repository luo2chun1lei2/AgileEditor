#-*- coding:utf-8 -*-

'''
Ide中每个被打开的文件。
'''

import os.path

class ModelFile(object):
    '''
    代表Ide中的一个被打开的文件。
    file_path:路径，如果是None，证明是新建的文件。
    file_obj:文件对象。
    file_buf:用于编辑器的buffer。
    文件状态必须是打开或者创建后，然后进行读写操作，再关闭。
    '''    
    def __init__(self):
        self.file_obj = None
        self.file_path = None
        self.file_buf = None
    
    def open_file(self, file_path):
        '''
        打开指定的文件。
        return:文件的file_obj.
        '''
        
        print('Open file ' + file_path)
        
        if(self.file_obj != None):
            print('File(%s) is open.', self.file_path)
            return None
        
        if os.path.exists(file_path):
            self.file_obj = open(file_path, 'r+')
        else: 
            self.file_obj = open(file_path, 'w+')
        
        self.file_path = file_path
        
        return self.file_obj
    
    def read_file(self, src_buffer):
        '''
        buffer: GtkSource.Buffer
        '''
        if self.file_obj == None:
            print('File is NOT open.')
            return

        src_buffer.begin_not_undoable_action()
        
        # 将文件中的数据放入Buffer中。
        # TODO: 对于大数据文件怎么办？
        src_buffer.delete(src_buffer.get_start_iter(), src_buffer.get_end_iter())
        
        for line in self.file_obj:
            #print("" + line)
            src_buffer.insert(src_buffer.get_end_iter() ,line)
        
        # 可以禁止undo动作。
        src_buffer.end_not_undoable_action()
            
    def save_file(self, src_buffer):
        '''
        src_buffer:GtkSource.Buffer
        '''
        if self.file_obj == None:
            print('File is Not opened.')
            return
            
        text = src_buffer.get_text(src_buffer.get_start_iter(), src_buffer.get_end_iter(), False)

        # 删除原来的数据，然后写入新的数据
        self.file_obj.truncate(0)
        self.file_obj.seek(0, 0)
        self.file_obj.write(text)
        self.file_obj.flush()
    
    def close_file(self):
        if(self.file_obj != None):
            self.file_obj.close()
            self.file_obj = None
            self.file_path = None
    
    
