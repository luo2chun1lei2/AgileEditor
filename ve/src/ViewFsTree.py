#-*- coding:utf-8 -*-

# 显示文件系统列表。
# 显示的项目可以和当前打开的文件相互匹配。
# TODO 
# 1，不能自动监视文件系统的变化，不能添加、删除、修改文件，显示文件的信息。
# 2，排序要先文件夹，再文件。
# 3, 过滤部分文件。

import os, stat, time, collections, logging
from collections import OrderedDict

from gi.repository import GObject, Gtk, Gdk, GtkSource, GLib, GdkPixbuf
from bzrlib.tree import Tree

# 文件夹的图标。 
folderxpm = [
    "17 16 7 1",
    "  c #000000",
    ". c #808000",
    "X c yellow",
    "o c #808080",
    "O c #c0c0c0",
    "+ c white",
    "@ c None",
    "@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@",
    "@@+XXXX.@@@@@@@@@",
    "@+OOOOOO.@@@@@@@@",
    "@+OXOXOXOXOXOXO. ",
    "@+XOXOXOXOXOXOX. ",
    "@+OXOXOXOXOXOXO. ",
    "@+XOXOXOXOXOXOX. ",
    "@+OXOXOXOXOXOXO. ",
    "@+XOXOXOXOXOXOX. ",
    "@+OXOXOXOXOXOXO. ",
    "@+XOXOXOXOXOXOX. ",
    "@+OOOOOOOOOOOOO. ",
    "@                ",
    "@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@"
    ]
folderpb = GdkPixbuf.Pixbuf.new_from_xpm_data(folderxpm)

# 文件的图标。
filexpm = [
    "12 12 3 1",
    "  c #000000",
    ". c #ffff04",
    "X c #b2c0dc",
    "X        XXX",
    "X ...... XXX",
    "X ......   X",
    "X .    ... X",
    "X ........ X",
    "X .   .... X",
    "X ........ X",
    "X .     .. X",
    "X ........ X",
    "X .     .. X",
    "X ........ X",
    "X          X"
    ]
filepb = GdkPixbuf.Pixbuf.new_from_xpm_data(filexpm)

class FsTreeModel(GObject.GObject, Gtk.TreeModel):
    # 文件列表模型，是TreeView的TreeModel的一个实现。
    
    __gtype_name__ = 'FsTreeModel'
    # 新类型的名字，GTK新类型必须有的。
    
    column_types = (GdkPixbuf.Pixbuf, str, int, str, str, str)
    # 列的类型，因为第一项和第二项联合显示，所以后面column_names和columns_visibles比这个少一个。
    
    column_names = ['文件名字 ', '大小', '模式', '最后修改时间', '绝对路径']
    # 列的标题
    
    column_visibles = [True, False, False, False, False]
    # 列是否显示

    def __init__(self, dir_path=None):
        # dir_path:string:文件夹的路径，如果没有设定，就是空的目录。 

        GObject.GObject.__init__(self)
        
        # TODO:在TreeIter中只能保存Int类型的参数（放string不行吗？），所以需要用id将object类型转成int的一个索引号，
        # 然后在pool中保存，但是没有地方释放！
        # 对策：以后可以变成包含文件路径和TreeIter的数据，这样可以节约TreeIter。
        self.pool = {}
        
        if dir_path:
            self.dir_path = os.path.abspath(dir_path)
            # 得到整个目录中的文件和子文件夹，以及其下的所有文件。
            # TODO: 是否应该懒加载？
            self.files = self._build_file_dict(self.dir_path)
        else:
            self.dir_path = None
            
    # TODO:以后文件越来越多，应该修改成使用时才打开。
    def _build_file_dict(self, dirname):
        # 生成dirname目录下面的所有文件的列表，包括子目录。
        # Returns
        # A dictionary containing the files in the given dir_path keyed by filename.
        # If the child filename is a sub-directory, the dict value is a dict. Otherwise it will be None.

        d1 = OrderedDict()
        d2 = OrderedDict()
        
        if os.access(dirname, os.R_OK):
            for fname in os.listdir(dirname):
                path = os.path.join(dirname, fname)
                #print "---> path %s" % path
                try:
                    filestat = os.stat(path)
                except OSError:
                    d2[fname] = None
                else:
                    if fname == '.':
                        continue
                    elif fname == '..':
                        continue
                    elif fname.startswith('.'):
                        # 忽略隐藏文件
                        continue
                    # 下面加入过滤 TODO 以后可以加入SETTING
                    elif fname.endswith('.o') or fname.endswith('.a'):
                        continue
                    elif fname == "GPATH" or fname == "GRTAGS" or fname == "GSYMS" or fname == "GTAGS":
                        continue
                    else :
                        if stat.S_ISDIR(filestat.st_mode):
                            d1[fname] = self._build_file_dict(path)
                        else:
                            d2[fname] = None

        d1 = collections.OrderedDict(sorted(d1.items(),key = lambda t:t[0]))
        d2 = collections.OrderedDict(sorted(d2.items(),key = lambda t:t[0]))
        d1.update(d2)
        
        return d1
    
    def get_column_names(self):
        # 得到列的标题名字。
        # return:[String]:每列的名字数组
        
        return self.column_names[:]
    
    def get_column_visible(self):
        # 得到列是否显示。
        # return:[Bool]:每列是否显示的数组
        
        return self.column_visibles[:]
    
    def _save_tp_in_iter(self, iter, tree_path):
        # 将TreePath保存到TreeIter中，另外缓存。
        
        str = tree_path.to_string()
        iter.user_data = id(str)
        self.pool[iter.user_data] = str
        
    def _get_tp_in_iter(self, iter):
        # 将Tree Path从TreeIter中取出来。
        # iter:Gtk.TreeIter:目前Tree的迭代子
        # return:Gtk.TreePath:得到Tree的TreePath
        
        if iter.user_data not in self.pool:
            logging.error('index %d not in pool' % (iter.user_data))
            return None
        
        str_tree_path = self.pool[iter.user_data]
        
        return Gtk.TreePath.new_from_string(str_tree_path)

    def _get_fp_from_tp(self, tree_path):
        # 根据 tree path 得到实际的路径（不是绝对路径）。
        # tree_path:Gtk.TreePath:TreePath
        # return:String:文件的路径，None，非法情况
        
        file_path = ''
        file_node = self.files
        
        indices = tree_path.get_indices()
        for index in indices:
            if file_node is None:
                # 这个是非法的Tree Path
                return None
            else:
                nodes = file_node.items()
                if index >= len(nodes):
                    # 这个是非法的Tree Path
                    return None
                else:
                    k, v = nodes[index]
                    file_path = os.path.join(file_path, k)
                    file_node = v

        if file_path == '':
            return None
        else:
            return file_path
    
    def _get_fp_from_iter(self, iter):
        # 由TreeIter得到File path
        tree_path = self.get_path(iter)
        return self._get_fp_from_tp(tree_path)
    
    def get_abs_filepath(self, filepath):
        # 根据相对路径，得到文件的绝对路径
        # filepath:string:相对路径
        # return:string:绝对路径
        return os.path.join(self.dir_path, filepath)
    
    def _tp_is_ok(self, tree_path):
        # 判断 tree path是否正确
        # 如果根据tree path得到真正的文件路径，就认为是合法的。
        # return:Bool:True,OK，False，错误。
        
        fp = self._get_fp_from_tp(tree_path)
        return (fp is not None)
    
    def _get_node_from_tp(self, tree_path):
        # 根据Tree Path得到所在的（Key，Value），
        #return Key是文件名字，
        #       Value是文件下面的子文件夹。
        
        file_item = None
        file_node = self.files
        
        indices = tree_path.get_indices()
        for index in indices:
            if file_node is None:
                # 这个是非法的Tree Path
                return None
            else:
                nodes = file_node.items()
                if index >= len(nodes):
                    # 这个是非法的Tree Path
                    return None
                else:
                    file_item = nodes[index]
                    file_node = file_item[1]    # value

        return file_item

    def is_folder(self, tree_path):
        # 判断指定的路径是否为文件夹。
        # path:Gtk.TreePath:
        # return:Bool:true是, False 否。 
        
        file_node = self._get_node_from_tp(tree_path)
        if file_node is None:
            return False
        else:
            return (file_node[1] is not None)
    
    def get_n_children_of_tp(self, tree_path):
        # 根据tree_path对应的文件下面的子文件数目。
        # tree_path:Gtk.TreePath:TreePath
        # return:int:子文件的数量。
        
        file_node = self._get_node_from_tp(tree_path)
        if file_node is None:
            return 0
        else:
            return len(file_node[1])
        
    def get_tree_path_by_rel_file_path(self, rel_file_path):
        # 根据文件的相对路径，得到TreePath
        # rel_file_path:string:相对路径
        # return:Gtk.TreePath:TreePath
        
        tree_path = Gtk.TreePath.new()
        node = self.files
        for key in rel_file_path.split(os.path.sep):
            tree_path.append_index(list(node.keys()).index(key))
            node = node[key]
        return tree_path

    #######################################################
    ## TreeModel Implementation
    
    def do_get_n_columns(self):
        # 返回当前栏目的数目
        return len(self.column_types)
    
    def do_get_column_type(self, index_):
        # 返回此栏的类型。
        # return:GObject.GType:
        
        return self.column_types[index_]

    def do_get_flags(self):
        #return:Gtk.TreeModelFlags:是下面的值的 |，设定后，不可修改。 
        # ITERS_PERSIST = 1  iterators survive all signals emitted by the tree
        # LIST_ONLY = 2 the model is a list only, and never has children

        return Gtk.TreeModelFlags.ITERS_PERSIST
     
    def do_get_iter(self, tree_path):
        # 创建指定此路径的枚举器，并返回。
        # tree_path:Gtk.TreePath:需要检查是否有效。
        # return:bool,GtkTreeIter:如果成功，就返回True和对应的Iter，如果没有就返回False和一个无效的Iter。
        
        if not self._tp_is_ok(tree_path):
            logging.error("Cannot get iter of %s" % tree_path)
            return False, None

        itr = Gtk.TreeIter()
        self._save_tp_in_iter(itr, tree_path)
        
        return True, itr
 
    def do_get_path(self, itr):
        # 得到一个新创建的TreePath，根据itr。
        # itr:GtkTreeIter:
        # return:Gtk.TreePath:
        
        tree_path = self._get_tp_in_iter(itr)
        return tree_path
 
    def do_get_value(self, iter, column):
        # 根据路径显示不同栏的信息
        # iter:Gtk.TreeIter:
        # column:int:查看的栏
        # return:GObject.Value:这个枚举器对应的值
        
        # 根据iter得到当前的文件的相对路径(相对于基础路径)
        filepath = self._get_fp_from_iter(iter)

        # 得到绝对路径
        abs_path = self.get_abs_filepath(filepath)
        try:
            filestat = os.stat(abs_path)
        except OSError:
            return None
        mode = filestat.st_mode
        if column is 0: # 是否文件夹
            if stat.S_ISDIR(mode):
                return folderpb
            else:
                return filepb
        elif column is 1:   # 文件/文件夹名字
            return os.path.basename(filepath)
        elif column is 2:   # 文件大小
            return filestat.st_size
        elif column is 3:   # 文件权限
            return oct(stat.S_IMODE(mode))
        elif column is 4:   # 文件的最后修改时间 
            return time.ctime(filestat.st_mtime)
        elif column is 5: # 文件绝对路径(不显示)
            return abs_path
          
        return ""
     
    def do_iter_children(self, parent):
        # 获取parent的第一个子枚举器，如果parent是空，那么返回第一个子，如果parent下面是空，就返回false,None。
        # parent:Gtk.TreeIter:可能是None
        # return:bool,Gtk.TreeIter: 
        
        tree_path = None
        
        if parent is None:
            # 是第一层的节点，所以Parent是None,只要返回第一个节点就可以了
            tree_path = Gtk.TreePath.new_first()
        else:
            tree_path = self.get_path(parent)
            tree_path.down()

        if self._tp_is_ok(tree_path):
            # 还需要判断第一个文件是否存在。
            it = Gtk.TreeIter()
            self._save_tp_in_iter(it, tree_path)
            return True, it
        else:
            logging.error("Can not get children.")
            return False, None
     
    def do_iter_has_child(self, iter):
        # 看看iter是否有子。
        # iter:Gtk.TreeIter:
        # return:Bool:是否有。
        
        tree_path = self.get_path(iter)
        if tree_path is None:
            logging.error("Has no child")
            return False
        else:
            # TODO 空文件夹怎么办？
            return self.is_folder(tree_path)

    def do_iter_n_children(self, iter):
        # 返回iter下面的子的数目。 TODO:没有调用？怎么会？
        # iter:Gtk.TreeIter
        # return:int:子文件的数量。
        
        tree_path = self.get_path(iter)
        return self.get_n_children_of_tp(tree_path)
    
    def do_iter_nth_child(self, parent, n):
        # 得到parent下面的第N个子。如果parent是None，则是root的第几个。
        # parent TreeIter
        # return (bool, Gtk.TreeIter)
        
        tree_path = None
        
        if parent is None:
            tree_path = Gtk.TreePath.new_from_string(str(n))
        else:
            tree_path = self._get_tp_in_iter(parent)
            if tree_path is None:
                logging.error("tree_path is None. %d" % n)
                return False, None
            tree_path.append_index(n)
            
        if self._tp_is_ok(tree_path):
            it = Gtk.TreeIter()
            self._save_tp_in_iter(it, tree_path)
            return True, it
        else:
            # 没有下一个
            logging.error("Can not get No. %d child." % n)
            self._tp_is_ok(tree_path)
            return False, None

    def do_iter_next(self, iter):
        # 设定iter到下一个。
        # return:bool:False, 如果没有了。
        
        tree_path = self._get_tp_in_iter(iter)
        if tree_path is None:
            return False
        
        tree_path.next()
        if self._tp_is_ok(tree_path):
            self._save_tp_in_iter(iter, tree_path)
            return True
        else:
            # 没有下一个
            return False

    def do_iter_previous(self, iter):
        # 得到iter的上一个Iter。
        # return:bool:
        
        tree_path = self._get_tp_in_iter(iter)
        tree_path.next
        if tree_path.prev() :
            self._save_tp_in_iter(iter, tree_path)
            return True
        else :
            # 没有下一个
            return False
    
    def do_iter_parent(self, child):
        # 得到child的上一级节点。
        # child:Gtk.TreeIter:
        # return:bool,Gtk.TreeIter:
        
        tree_path = self._get_tp_in_iter(child)
        if tree_path is None:
                return False, None
            
        if tree_path.up():
            itr = Gtk.TreeIter()
            self._save_tp_in_iter(itr, tree_path)
            return True, itr
        else:
            logging.error("Can not get Parent iterator.")
            return False, None

# 需要注册这个对象到GObject中。
GObject.type_register(FsTreeModel)

# TODO:目前这个不是一个控件，希望以后变成一个控件。
class ViewFsTree:
    # 初始化文件系统列表控件。
    # 外部是滚动条，内部是ListView。
    
    TARGETS = [
              ('MY_TREE_MODEL_ROW', Gtk.TargetFlags.SAME_APP, 0),
              ('text/plain', 0, 1),
              ('TEXT', 0, 2),
              ('STRING', 0, 3),
              ]
    
    def __init__(self):

        # 创建文件系统的模型。
        self.listmodel = FsTreeModel()

        # 创建TreeView。
        self.treeview = Gtk.TreeView()
        
        ## 允许拖拽 TODO 无用，好像只能使用TreeStore和ListStore才行。
        self.treeview.set_reorderable(True)
        self.treeview.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, 
                                               self.TARGETS, 
                                               Gdk.DragAction.DEFAULT | Gdk.DragAction.MOVE)
        self.treeview.enable_model_drag_dest(self.TARGETS, Gdk.DragAction.DEFAULT)
        self.treeview.connect("drag-data-received", self.on_drag_data_received)
        self.treeview.connect("drag_data_get", self.on_drag_data_get_data)

        # create the TreeViewColumns to display the data
        column_names = self.listmodel.get_column_names()
        column_visibles = self.listmodel.get_column_visible()
        self.tvcolumn = [None] * len(column_names)
        
        # 第一列（图标+文件名字）
        self.tvcolumn[0] = Gtk.TreeViewColumn(column_names[0])
        self.tvcolumn[0].set_alignment(0.5) # 标题的对齐
        
        cellpb = Gtk.CellRendererPixbuf()
        self.tvcolumn[0].pack_start(cellpb, False)
        self.tvcolumn[0].add_attribute(cellpb, 'pixbuf', 0)
        
        cell = Gtk.CellRendererText()
        self.tvcolumn[0].pack_start(cell, True)
        self.tvcolumn[0].add_attribute(cell, 'text', 1)
        self.tvcolumn[0].set_visible(column_visibles[0])
        self.treeview.append_column(self.tvcolumn[0])
        
        # 从第二列开始
        for n in range(1, len(column_names)):
            cell = Gtk.CellRendererText()
            if n == 1:
                cell.set_property('xalign', 1.0) # 右对齐
            self.tvcolumn[n] = Gtk.TreeViewColumn(column_names[n], cell, text=n + 1)
            self.tvcolumn[n].set_visible(column_visibles[n])
            self.treeview.append_column(self.tvcolumn[n])

        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        
        self.scrolledwindow.add(self.treeview)
        
        # 自定义的。
        self.scrolledwindow.set_size_request(150, 0)
        self.treeview.set_activate_on_single_click(False)
        
        #这个时候还没有设定项目的目录，所以没有必要设定list model.
        #self.treeview.set_model(self.listmodel)
        
    def on_drag_data_received(self, widget, drag_context, x, y, selection_data, info, timestamp):
        pass
    
    def on_drag_data_get_data(self, treeview, context, selection, target_id, etime):
        pass
    
    def show_file(self, abs_file_path):
        # 将当前焦点切换到指定的文件上。
        
        model = self.treeview.get_model()
        if not abs_file_path.startswith( model.dir_path ):
            # 不是这个目录下的文件
            return 
        
        rel_path = abs_file_path[len(model.dir_path) + 1:]
        tree_path = model.get_tree_path_by_rel_file_path(rel_path)
        
        # 展开
        self.treeview.expand_to_path(tree_path)
        # 选中
        self.treeview.set_cursor(tree_path)
        
    def get_file_path_by_iter(self, itr):
        # 根据iter得到文件的相对路径
        # iter:Gtk.TreeIter:Iterator
        # return:String:文件的相对路径
        model = self.treeview.get_model()
        return model._get_fp_from_iter(itr)
    
    def get_abs_file_path_by_iter(self, itr):
        # 根据iter得到文件的绝对路径
        # iter:Gtk.TreeIter:Iterator
        # return:String:文件的绝对路径
        model = self.treeview.get_model()
        fp = model._get_fp_from_iter(itr)
        return model.get_abs_filepath(fp)
    
    # TODO 感觉上不应该这样实现，而应该修改完文件后，刷新Tree
    def refresh_line(self, itr):
        # 更新指定itr和之下的所有数据
        # itr:Gtk.TreeIter:iterator
        # return:Nothing
        pass #TODO 没有实现。

    def set_model(self, model):
        # 设定Tree的Model
        # model:TreeModel:
        # return:Nothing
        self.treeview.set_model(model)
        
    def get_view(self):
        # 返回外部需要包含的控件
        # return:Gtk.Widget:
        return self.scrolledwindow
    
    def get_treeview(self):
        # 返回TreeView控件
        # return:TreeView:
        return self.treeview
    