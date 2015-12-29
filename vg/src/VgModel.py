#-*- coding:utf-8 -*-

''' 记录命令和对应的结果。'''

import random

class VgPiece:
    
    (
    STATE_EMPTY,
    STATE_SELECTED,
    STATE_UNSELECTED,
    ) = range(3)
    
    def __init__(self, row, col, state, num):
        self.row = row
        self.col = col
        self.state = state
        self.num = num
        self.checked = False    # 供以后检查使用。
        
    def get_text(self):
        return '%d' % (self.num)

class VgModel:
    
    my_instance = None
    
    def __init__(self):
        # 每个单元是行，每个行中又包含列信息，然后才是Piece信息。
        self.list = []
        # 行数
        self.n_row = 0
        # 列数
        self.n_col = 0
        # 最多可以选择的数目
        self.max_selected = 4
        
        # 棋子中最大的绝对值
        self.max_num = 4
        
    @staticmethod
    def instance():
        if VgModel.my_instance is None:
            VgModel.my_instance = VgModel()
            
        return VgModel.my_instance
    
    def create(self, row_count, col_count):
        self.n_row = row_count
        self.n_col = col_count
        
        mix_data = self._mix(self.n_row, self.n_col)
        
        self.list = []
        self.sum = 0
        for row in range(0, self.n_row):
            row_data = []
            for col in range(0, self.n_col):
                num = mix_data[row * self.n_col + col]
                row_data.append(VgPiece(row+1, col+1, VgPiece.STATE_UNSELECTED, num))
            self.list.append(row_data)
            
        return self.list
    
    def get_piece(self, row, col):
        if row < 1 or row > self.n_row:
            return None
        elif col < 1 or col > self.n_col:
            return None
        
        return self.list[row-1][col-1]
    
    def change_selected(self, row, col):
        piece = self.get_piece(row, col)
        
        if piece.state == VgPiece.STATE_SELECTED:
            self._unselected(row, col)
            self._calculate()
            return True # 无论如何都要更新
        
        elif piece.state == VgPiece.STATE_UNSELECTED:
            selected_count = len(self._get_selected_list())
            if selected_count >= self.max_selected:
                return False
            else:
                self._selected(row, col)
                self._calculate()
                return True
            
        elif piece.state == VgPiece.STATE_EMPTY:
            return False
        
    def _selected(self, row, col):
        piece = self.get_piece(row, col)
        piece.state = VgPiece.STATE_SELECTED
        
    def _unselected(self, row, col):
        piece = self.get_piece(row, col)
        piece.state = VgPiece.STATE_UNSELECTED
        
    def _set_empy(self, row, col):
        piece = self.get_piece(row, col)
        piece.state = VgPiece.STATE_EMPTY
    
    def _mix(self, nrow, ncol):
        s = nrow * ncol
        data_sum = 0
        data = []
        for i in range(0, s):
            num = random.randint(1, self.max_num)
            if random.randint(1, 2) == 1:
                num = -num
            
            data_sum += num
            data.append(num)

        # 需要配零
        if data_sum != 0:
            # 为了配零，需要反过来
            if data_sum < 0:
                frag = 1
            else:
                frag = -1
                
            for i in range(0, abs(data_sum)):
                while(True):
                    index = random.randint(0, s-1)
                    num = data[index] + frag
                    if abs(num) <= self.max_num and num != 0:
                        data[index] = num
                        break
        
        return data

    def _calculate(self):
        ''' 
        \return 是否需要更新画面
        '''
        selected_list = self._get_selected_list()
        
        # 检查个数
        if len(selected_list) == 0:
            return
        if len(selected_list) > self.max_selected:
            return
        
        # 检查是否连通。
        
        # -根据棋盘计算得到选中点的连通数据结构
        link_list = []
        for i in range(0, len(selected_list)):
            f = selected_list[i]
            for j in range(i+1, len(selected_list)):
                to = selected_list[j]
                
                if self.is_linked(f, to):
                    link_list.append( (i, j) )

        # 从其中的一个点遍历整个连接点，如果最后连通的数目等同于选中的棋子数目，就是都连通的。
        founds = self._travel_link_list(link_list)
                    
        if len(founds) != len(selected_list):
            # 这些点之间没有连通
            return

        # 检查和是否等于0
        sum = 0
        for piece in selected_list:
            sum += piece.num
            
        if sum != 0:
            return
    
        # 如果成功，就设定为空。
        for piece in selected_list:
            piece.state = VgPiece.STATE_EMPTY
    
    def _get_selected_list(self):
        selected_list = []
        for row in range(0, self.n_row):
            for col in range(0, self.n_col):
                piece = self.get_piece(row+1, col+1)
                if piece.state == VgPiece.STATE_SELECTED:
                    selected_list.append(piece)
            
        return selected_list
    
    def _travel_link_list(self, link_list):
        founds = []
        stack = []
        
        stack.append(0)
        while len(stack) != 0:
            #self._travel_link_list(founds, stack, link_list)
            p = stack.pop()
            founds.append(p)
            
            for (f, t) in link_list:
                if p == f:
                    if t not in founds:
                        stack.append(t)
                elif p == t:
                    if t not in founds:
                        stack.append(f)
                        
        return founds
    
    def is_linked(self, f, t):
        ''' 检查两个节点之间是否相连。 '''
        
        # 首先清除检查标记
        self._clean_check()
        
        f.check = True
        
        stack = []
        stack.append(f)
            
        #顺着栈，检查所有空白相邻的节点是否是t
        while len(stack) != 0:
            p = stack.pop()
            if self.check_4(stack, p, t):
                return True
            
        return False
        
    def check_4(self, stack, f, t):
        ''' 检查P的四个方向 '''
        # 检查from的四个相邻的单元，如果是空白，就放入栈中
        p = self._up(f)
        if self._is_t(stack, p, t):
            return True
        
        p = self._down(f)
        if self._is_t(stack, p, t):
            return True
        
        p = self._left(f)
        if self._is_t(stack, p, t):
            return True
        
        p = self._right(f)
        if self._is_t(stack, p, t):
            return True
        
    def _is_t(self, stack, p, t):
        if p is None:
            return False
        elif p.checked == True:
            return False
        elif p.state == VgPiece.STATE_EMPTY:
            p.checked = True
            stack.append(p)
            return False
        elif p is t:
            return True
        else:
            return False
    
    def _up(self, p):
        return self.get_piece(p.row-1, p.col)
    
    def _down(self, p):
        return self.get_piece(p.row+1, p.col)
    
    def _left(self, p):
        return self.get_piece(p.row, p.col-1)
    
    def _right(self, p):
        return self.get_piece(p.row, p.col+1)
    
    def _clean_check(self):
        for row in range(0, self.n_row):
            for col in range(0, self.n_col):
                piece = self.get_piece(row+1, col+1)
                piece.checked = False
        