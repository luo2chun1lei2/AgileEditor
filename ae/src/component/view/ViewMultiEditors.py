# -*- coding:utf-8 -*-

#######################################
# 画面：显示多个编辑器的图形界面

import os, sys, getopt, logging
from collections import OrderedDict
from gi.repository import Gtk, Gdk, GtkSource, GLib, Pango, Gio

from framework.FwManager import FwManager
from component.model.ModelFile import ModelFile
from component.view.ViewMenu import ViewMenu
from framework.FwComponent import FwComponent
from framework.FwManager import FwManager
from component.util.UtilEditor import UtilEditor

class ViewEditor:
    # [模块内使用]一个编辑器的信息
    # editor:GtkSource.View:源代码的编辑器控件
    # ide_file:ModelFile:编辑的文件

    # 编辑器当前的状态。
    (
     EDITOR_STATUS_NO_MODIFIED,  # 文件没有被修改。
     EDITOR_STATUS_MODIFIED,  # 文件被修改了
     ) = range(2)

    def __init__(self, editor, ide_file):
        self.editor = editor
        self.ide_file = ide_file

class ViewMultiEditors(FwComponent):
    # 内部管理多个打开文件的编辑器，可以
    # 1, 打开一个文件，如果已经存在，就显示已经打开的。
    # 2, 关闭一个文件。
    # 3, 得到当前编辑的文件。

    # notebook Gtk.NoteBook 管理多个控件的Tab Page控件。
    # 文件名字为“”，表明是一个新文件，且所有的新文件都是一个。
    # dic_editors [str, ViewEditor] 数组：文件路径（绝对），编辑器

    def __init__(self):
        super(ViewMultiEditors, self).__init__()

        self.styleScheme = None

        # 生成Tab page 类型的控件。
        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.connect("switch_page", self.on_switch_page)
        self.notebook.connect("page-reordered", self.on_page_reordered)

        # 包含文件信息和编辑器的信息字典，Key是文件绝对路径
        self.dic_editors = OrderedDict()

    # override component
    def onRegistered(self, manager):
        # TODO get 类型的服务太多，而且重复了，所以应该将属于editors的功能移入到这里类中，然后做一个封装！
        info = [{'name':'view.multi_editors.get_view', 'help':'get view of multiple editors.'},
                {'name':'view.multi_editors.open_editor', 'help':'open one editor.'},
                {'name':'view.multi_editors.close_editor', 'help':'close one editor.'},
                {'name':'view.multi_editors.get_editor_by_path', 'help':'get current editor by path.'},
                {'name':'view.multi_editors.get_current_editor', 'help':'get current editor.'},
                {'name':'view.multi_editors.get_current_ide_editor', 'help':'get current editor.'},
                {'name':'view.multi_editors.get_current_abs_file_path', 'help':'get absolutive path of current file.'},
                {'name':'view.multi_editors.get_current_ide_file', 'help':'show model of current file.'},
                {'name':'view.multi_editors.change_editor_style', 'help':'change the style scheme of editors.'},
                {'name':'view.multi_editors.change_editor_font', 'help':'change the font of editors.'}]
        manager.register_service(info, self)
        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "view.multi_editors.get_view":
            return (True, {'view': self.get_tab_page()})
        elif serviceName == "view.multi_editors.open_editor":
            self.show_editor(params['abs_file_path'])
            return True, None
        elif serviceName == "view.multi_editors.close_editor":
            self.close_editor(params['abs_file_path'])
            return True, None
        elif serviceName == "view.multi_editors.get_editor_by_path":
            return (True, {'editor': self.get_editor_by_path(params['abs_file_path'])})
        elif serviceName == "view.multi_editors.get_current_editor":
            return (True, {'editor': self.get_current_editor()})
        elif serviceName == "view.multi_editors.get_current_ide_editor":
            return (True, {'editor': self.get_current_ide_editor()})
        elif serviceName == "view.multi_editors.get_current_abs_file_path":
            return (True, {'abs_file_path': self.get_current_abs_file_path()})
        elif serviceName == "view.multi_editors.get_current_ide_file":
            return (True, {'ide_file': self.get_current_ide_file()})

        elif serviceName == "view.multi_editors.change_editor_style":
            self.changeEditorStyle(params['style'])
            return (True, None)
        elif serviceName == "view.multi_editors.change_editor_font":
            self.changeEditorFont(params['font'])
            return (True, None)

        else:
            return (False, None)

    def set_tab_label_by_state(self, label, abs_file_path, is_modified):

        title = os.path.basename(abs_file_path)
        if is_modified:
            title = "<span foreground='red'>" + title + " *</span>"
        else:
            title = "<span foreground='black'>" + title + "</span>"

        label.set_markup(title)

    def get_tab_page(self):
        # 得到内部的Tab Page控件。
        return self.notebook

    def get_current_editor(self):
        # 得到当前的编辑器。
        # 如果没有打开的编辑器，就返回None

        index = self.notebook.get_current_page()
        if index < 0 :
            return None

        oneEditor = self.dic_editors.values()[index]

        return oneEditor.editor

    def get_current_ide_file(self):
        # 得到当前的编辑器编辑的文件。
        # return ModelFile 编辑的文件，None：如果不存在

        index = self.notebook.get_current_page()
        if index < 0 :
            return None

        oneEditor = self.dic_editors.values()[index]

        return oneEditor.ide_file

    def get_editor_by_path(self, abs_file_path):
        index = self._index_of_path(abs_file_path)
        if index < 0 :
            return None

        oneEditor = self.dic_editors.values()[index]

        return oneEditor

    def get_current_ide_editor(self):
        # 得到当前的编辑器编辑的文件。
        # return ModelFile 编辑的文件，None：如果不存在

        index = self.notebook.get_current_page()
        if index < 0 :
            return None

        oneEditor = self.dic_editors.values()[index]

        return oneEditor

    def get_current_abs_file_path(self):
        index = self.notebook.get_current_page()
        if index < 0 :
            return None

        abs_file_path = self.dic_editors.keys()[index]
        return abs_file_path

    def show_editor(self, abs_file_path):
        # 显示一个文件在编辑器中，
        # 如果文件已经打开，显示此文件的编辑器放在最前面。
        # 如果没有打开，就打开。

        if abs_file_path in self.dic_editors:  # 文件已经打开过
            current_file_path = self.get_current_abs_file_path()
            if current_file_path == abs_file_path:
                # 当前打开的文件正是此文件，就无需再打开。
                return

        else:  # 文件没有打开过。
            # - 编辑器（在滚动条内）
            # 打开并且读取文件内容到编辑器
            ide_file = ModelFile()
            ide_file.open_file(abs_file_path)

            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

            scrolledCtrl, editor = self._create_editor()
            #editor.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(1, 0, 0))
            scrolledCtrl.set_size_request(200, 0)

            self._ide_only_open_file(ide_file, abs_file_path, editor)

            # - 状态栏
            status_bar = Gtk.Statusbar.new()
            # 通过设置 margin，改变高度。
            status_bar.set_margin_top(0)
            status_bar.set_margin_bottom(0)
            editor.get_buffer().connect("changed", self.on_buffer_changed, status_bar)  # 为了显示状态栏
            editor.get_buffer().connect("mark-set", self.on_buffer_mark_set, status_bar)  # 为了显示状态栏

            vbox.pack_start(scrolledCtrl, True, True, 0)
            vbox.pack_start(status_bar, False, False, 0)

            # 一定要调用加入Notebook的控件的show方法，才能显示。
            editor.show()
            scrolledCtrl.show()
            status_bar.show()
            vbox.show()

            tab_label = Gtk.Label()
            self.set_tab_label_by_state(tab_label, abs_file_path, False)
            index = self.notebook.append_page(vbox, tab_label)

            # 允许调整位置.
            self.notebook.set_tab_reorderable(self.notebook.get_nth_page(index), True)

            self.dic_editors[abs_file_path] = ViewEditor(editor, ide_file)

            editor.get_buffer().connect("modified-changed", self.on_editor_buffer_modified_changed, abs_file_path)

        index = self._index_of_path(abs_file_path)

        self.notebook.set_current_page(index)

    def on_buffer_changed(self, src_buf, statusbar):
        mark = src_buf.get_mark("insert")
        location = src_buf.get_iter_at_mark(mark)
        line_end = location.copy()
        if not line_end.ends_line():
            line_end.forward_to_line_end()
        self._ide_show_status(statusbar, location.get_line() + 1, src_buf.get_line_count(),
                              location.get_line_offset() + 1, line_end.get_line_offset() + 1)

    def on_buffer_mark_set(self, src_buf, location, mark, statusbar):
        if mark.get_name() == "insert":
            line_end = location.copy()
            if not line_end.ends_line():
                line_end.forward_to_line_end()
            self._ide_show_status(statusbar, location.get_line() + 1, src_buf.get_line_count(),
                                  location.get_line_offset() + 1, line_end.get_line_offset() + 1)

    def _ide_show_status(self, statusbar, row, total_row, column, total_column):
        statusbar.pop(0)
        msg = 'Line %4d/%4d, Column %3d/%3d' % (row, total_row, column, total_column)
        statusbar.push(0, msg)

    def _ide_only_open_file(self, ide_file, file_path, editor):

        self.freeze_editor(editor)

        src_buffer = editor.get_buffer()
        ide_file.read_file(src_buffer)
        UtilEditor.set_src_language(src_buffer, file_path)
        src_buffer.set_modified(False)

        self.unfreeze_editor(editor)

    def close_editor(self, abs_file_path):
        # 关闭对应的编辑器
        # abs_file_path:string:文件的绝对路径（作为唯一的标志）
        # return:Bool:False,关闭失败，比如没有这个文件，或者客户又选择不关闭。

        if not abs_file_path in self.dic_editors:
            return False

        oneEditor = self.dic_editors[abs_file_path]
        index = self._index_of_path(abs_file_path)

        self.notebook.remove_page(index)
        self.dic_editors.pop(abs_file_path)

        # 关闭文件
        oneEditor.ide_file.close_file()

    def freeze_editor(self, editor):
        # 冻结编辑器，暂时将completion禁止。
        completion = editor.props.completion
        completion.block_interactive()

    def unfreeze_editor(self, editor):
        # 解冻编辑器，将completion的禁止打开。
        completion = editor.props.completion
        completion.unblock_interactive()

    def _index_of_path(self, abs_file_path):

        index = 0
        for path in self.dic_editors.keys():
            if path == abs_file_path:
                return index
            index += 1

        return -1

    # 代码编辑器
    # 在滚动的控件内。
    def _create_editor(self):

        editor = GtkSource.View()

        editor.set_cursor_visible(True)
        editor.set_show_line_numbers(True)  # 显示行号
        editor.set_auto_indent(True)  # 自动缩进
        # editor.set_insert_spaces_instead_of_tabs(True) # 用空格代替tab
        editor.set_tab_width(4)  # tab宽度4
        editor.set_highlight_current_line(True)  # 高亮度显示当前行

        isOK, results = FwManager.instance().request_service('model.workshop.getopt', {'key': 'font'})
        self._ide_set_font(editor, results['value'])  # 设置字体。

        # 左边的标记区域
        gutter = editor.get_gutter(Gtk.TextWindowType.LEFT)
        gutter.set_padding(5, 0)

        src_buffer = self._create_buffer(None)
        editor.set_buffer(src_buffer)

        # 当在editor中按下mouse时，做一些处理。
        editor.connect('button-press-event', self.mouse_button_press_event_on_editor)

        scrolledCtrl = Gtk.ScrolledWindow()
        scrolledCtrl.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scrolledCtrl.set_hexpand(True)
        scrolledCtrl.set_vexpand(True)
        scrolledCtrl.add(editor)

        return (scrolledCtrl, editor)

    def _ide_set_font(self, widget, str_font_desc):
        # 设置控件的字体
        # widget Gtk.Widget 控件
        # str_font_desc String 字体的描述（名字 大小）

        font_desc = Pango.FontDescription.from_string(str_font_desc)
        widget.modify_font(font_desc)

    def _create_tag_table(self):
        tag_table = Gtk.TextTagTable.new()

        txt_tag = Gtk.TextTag.new('heading')
        txt_tag.set_property('weight', Pango.Weight.BOLD)
        txt_tag.set_property('size', 15 * Pango.SCALE)
        tag_table.add(txt_tag)

        txt_tag = Gtk.TextTag.new('bookmark')
        txt_tag.set_property('background', "red")
        tag_table.add(txt_tag)

        return tag_table

    def _create_buffer(self, file_path=None):

        # 支持的语言
        # ada awk boo c c-sharp changelog chdr cpp css d def desktop diff
        # docbook dot dpatch dtd eiffel erlang forth fortran gap gettext-translation
        # gtk-doc gtkrc haddock haskell haskell-literate html idl ini java js latex
        # libtool lua m4 makefile msil nemerle objc objective-caml ocl octave pascal
        # perl php pkgconfig python r rpmspec ruby scheme sh sql tcl texinfo vala vbnet
        # verilog vhdl xml xslt yacc

        manager = GtkSource.LanguageManager()

        tag_table = self._create_tag_table()
        src_buffer = GtkSource.Buffer.new(tag_table)

        # TODO:以后如果有算法，需要根据内容来判断文件的类型。
        if file_path is not None:
            language = manager.guess_language(file_path, None)  # 设定语法的类型
            src_buffer.set_language(language)
            src_buffer.set_highlight_syntax(True)  # 语法高亮

        if self.styleScheme is None:
            # 可以利用 styleSchemeManager.get_scheme_ids() 得到所有的id
            # ['cobalt', 'kate', 'oblivion', 'solarized-dark', 'solarized-light', 'tango', 'classic']
            isOK, results = FwManager.instance().request_service("model.workshop.getopt", {'key':"style"})

            styleSchemeManager = GtkSource.StyleSchemeManager.get_default()
            styleScheme = styleSchemeManager.get_scheme(results['value'])
            if styleScheme is not None:
                self.styleScheme = styleScheme  # 不能丢弃
                src_buffer.set_style_scheme(self.styleScheme)
        else:
            src_buffer.set_style_scheme(self.styleScheme)

        return src_buffer

    def on_switch_page(self, notebook, page, page_num):
        # 当切换Page时，发生，无论是用户手动还是编程方法调用。
        # page Gtk.Widget 切换到的页的控件
        # page_num int 切换到的页的索引

        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self._idle_on_switch_page, page_num)

    def _idle_on_switch_page(self, page_num):
        ''' 在IDLE时，执行的函数。
        '''
        if page_num > self.dic_editors.keys().count :
            return
        abs_file_path = self.dic_editors.keys()[page_num]

        FwManager.instance().send_event('view.multi_editors.switch_page', {'abs_file_path':abs_file_path})

    def on_page_reordered(self, notebook, child_view, page_num):
        # child_view is vbox, and his first child is ScrollView
        # TODO 这里实现并不好，非常依赖于画面的布局，希望进行修改。
        old_page_num = 0
        for editor in self.dic_editors.values():
            if editor.editor in child_view.get_children()[0].get_children():
                break
            old_page_num = old_page_num + 1

        # 将OrderedDict转化成数组，进行删除和添加操作。
        items = self.dic_editors.items()
        item = items.pop(old_page_num)
        items.insert(page_num, item)

        # 然后将变化后的数组再放入到OrderedDict中。
        new_dic = OrderedDict()

        for k, v in items:
            new_dic[k] = v

        # 将组件的引用修改成新的数据结构。
        self.dic_editors = new_dic

    def on_editor_buffer_modified_changed(self, src_buffer, abs_file_path):
        # 当文件是否修改被改变时

        index = self._index_of_path(abs_file_path)
        if index < 0:
            return

        child_page = self.notebook.get_nth_page(index)
        label = self.notebook.get_tab_label(child_page)

        self.set_tab_label_by_state(label, abs_file_path, src_buffer.get_modified())

    def changeEditorStyle(self, styleName):
        ''' 修改所有编辑器的 Style
        @param styleName: string: style name
        @return bool:is ok?
        '''
        styleSchemeManager = GtkSource.StyleSchemeManager.get_default()
        self.styleScheme = styleSchemeManager.get_scheme(styleName)  # 不能丢弃
        if self.styleScheme is None:
            logging.error("This style(%s) is NOT existed." % styleName)
            return False

        for viewEditor in self.dic_editors.values():
            srcBuffer = viewEditor.editor.get_buffer()
            srcBuffer.set_style_scheme(self.styleScheme)

        return True

    def changeEditorFont(self, fontName):
        ''' 修改所有编辑器的 font
        @param fontName: string: font name
        @return bool:is ok?
        '''

        for viewEditor in self.dic_editors.values():
            self._ide_set_font(viewEditor.editor, fontName)

        return True

    def mouse_button_press_event_on_editor(self, widget, event):
        if event.button == 8:
            # mouse's back, 9 is prev.
            FwManager.instance().request_service('ctrl.search.go_back_tag')
            return True
        elif event.button == 9:
            FwManager.instance().request_service('ctrl.search.go_forward_tag')
            return True

        return False
