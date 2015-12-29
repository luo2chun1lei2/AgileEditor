#-*- coding:utf-8 -*-

'''
显示命令的输出结果。
'''
import threading
from gi.repository import Gtk, Gdk, GObject, GLib, GtkSource, Pango

from VcEventPipe import *

class ViewLog:
    '''
    显示日志。
    1，来了新命令，是否更新当前的日志。
    2，命令来了新的日志，并显示后，是否滚动。
    '''
    
    # 设定一个栏目的枚举常量。
    (
     COLUMN_TAG_LINE_NO, # 行号
     COLUMN_TAG_NAME,  # Tag名字
     NUM_COLUMNS) = range(3)

    def __init__(self, vc_cmd_grp):

        self.vc_cmd_grp = vc_cmd_grp    # 当前执行的命令组
        self.vc_cmd = None      # 当前执行的命令

        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        editor = GtkSource.View()
        
        editor.set_cursor_visible(True)
        editor.set_show_line_numbers(True)              # 显示行号
        editor.set_auto_indent(True)                    # 自动缩进
        #editor.set_insert_spaces_instead_of_tabs(True) # 用空格代替tab
        editor.set_tab_width(4)                         # tab宽度4
        editor.set_highlight_current_line(True)         # 高亮度显示当前行
        editor.set_editable(False)                      # 只读
        
        self._ide_set_font(editor, "Ubuntu mono 12")    # 设置字体。
        
        src_buffer = self.create_buffer()
        editor.set_buffer(src_buffer) 
        
        sw.add(editor)

        self.view = sw
        self.taglistview = editor
        
        VcEventPipe.register_event(VcEventPipe.EVENT_LOG_COMMAND_START, self.sm_start_new_cmd)
        VcEventPipe.register_event(VcEventPipe.EVENT_LOG_APPEND_TEXT, self.sm_append_log)
        
        self.set_scrollable(True)
        self.set_show_new_cmd_log(True)
        
    def layout(self):
        self.taglistview.show()
        self.view.show()
    
    def unregister(self):
        VcEventPipe.unregister_event(VcEventPipe.EVENT_LOG_COMMAND_START, self.sm_start_new_cmd)
        VcEventPipe.unregister_event(VcEventPipe.EVENT_LOG_APPEND_TEXT, self.sm_append_log)
    
    def _ide_set_font(self, widget, str_font_desc):
        ''' 设置控件的字体
        widget Gtk.Widget 控件
        str_font_desc String 字体的描述（名字 大小）
        '''
        font_desc = Pango.FontDescription.from_string(str_font_desc)
        widget.modify_font(font_desc)
        
    def create_buffer(self):
        # TODO:寻找适合日志输出的语法。
        # 支持的语言
        # ada awk boo c c-sharp changelog chdr cpp css d def desktop diff 
        # docbook dot dpatch dtd eiffel erlang forth fortran gap gettext-translation 
        # gtk-doc gtkrc haddock haskell haskell-literate html idl ini java js latex 
        # libtool lua m4 makefile msil nemerle objc objective-caml ocl octave pascal 
        # perl php pkgconfig python r rpmspec ruby scheme sh sql tcl texinfo vala vbnet 
        # verilog vhdl xml xslt yacc
        
        src_buffer = GtkSource.Buffer()
        
        manager = GtkSource.LanguageManager()
        language = manager.get_language("sh")        # 设定语法的类型
        src_buffer.set_language(language)
        src_buffer.set_highlight_syntax(True)        # 语法高亮

        return src_buffer

    def set_scrollable(self, is_scrollable):
        # 更新日志后，不再滚动。
        self.is_scrollable = is_scrollable
            
        if is_scrollable: # 想滚动
            self._scroll_to_end()   # 马上滚动到最后
        else: #不想滚动
            pass # 什么都不用做。
            
    def get_scrollable(self, is_scrollable):
        # 查询当前是否滚动显示最新日志内容
        return self.is_scrollable
    
    def set_show_new_cmd_log(self, show):
        self.is_show_new_cmd_log = show
        
        if show:
            # 如果需要显示最新执行的命令日志，则需要更新当前的情况
            lastest_cmd = None
            for cmd in self.vc_cmd_grp.commands:
                if cmd.is_selected and cmd.process > 0:
                    lastest_cmd = cmd
            
            if lastest_cmd is not None:
                self.vc_cmd = lastest_cmd
                self.set_log(lastest_cmd)
        else:
            # 如果不再需要显示最新的命令日志，则什么都不用做
            pass

    def get_show_new_cmd_log(self):
        return self.is_show_new_cmd_log

    def sm_start_new_cmd(self, vc_cmd):
        # 如果命令不是这个命令组中的，就退出
        if vc_cmd not in self.vc_cmd_grp.commands:
            return
        
        # 如果不是当前命令，且不需要显示新的命令，则不再接受新的命令输出。
        if not self.is_show_new_cmd_log and self.vc_cmd != vc_cmd:
            return
        
        self.vc_cmd = vc_cmd
        
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.clean_log)
        
    def clean_log(self):
        ''' 将当前的文本清除 '''
        print "clean text"
        
        editor = self.taglistview
        src_buf = editor.get_buffer()
        
        src_buf.delete(src_buf.get_start_iter(), src_buf.get_end_iter())
        
    def sm_append_log(self, vc_cmd, text):
        # 如果命令不是这个命令组中的，就退出
        if vc_cmd not in self.vc_cmd_grp.commands:
            return
        
        # 如果不是当前命令，且不需要显示新的命令，则不再接受新的命令输出。
        if not self.is_show_new_cmd_log and self.vc_cmd != vc_cmd:
            return
        
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.append_log, text)
        
    def append_log(self, text):
        
#         thrd = threading.currentThread()
#         print "append text : %s" % ( thrd.getName() )
        #print "append " + text,
        
        ''' 添加一条信息。'''
        editor = self.taglistview
        src_buf = editor.get_buffer()
        
        iter_ = src_buf.get_end_iter()
        src_buf.insert(iter_, text)
        
        if self.is_scrollable:
            self._scroll_to_end()

    def set_log(self, vc_cmd):
        
        self.vc_cmd = vc_cmd
        self.set_show_new_cmd_log(False)
        
        self.clean_log()
        self.append_log(vc_cmd.get_log())
    
    def _scroll_to_end(self):
        
        editor = self.taglistview
        src_buf = editor.get_buffer()
        iter_ = src_buf.get_end_iter()
        # 移动到最后。(TODO:没有移动到最后)
        editor.scroll_to_iter(iter_, 0.25, False, 0.0, 0.5)