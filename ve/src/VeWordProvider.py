#-*- coding:utf-8 -*-

# 提供单词补全的功能。

import os, ConfigParser

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0') 
from gi.repository import GObject, Gtk, Gdk, GtkSource

from VeUtils import *
from ModelTags import ModelGTags

# 说明
# do_get_start_iter 和 GtkSource.CompletionContext.get_iter() 在最新的Ubuntu 16中修改了，
# 所以需要进行区别，用环境变量GTKSOURCE_COMPLETION_PROVIDER来代替。
#     新的是 gir1.2-gtksource-3.0 安装版本 3.18.2-1
#     旧的是 gir1.2-gtksource-3.0 安装版本 3.10.2-0ubuntu1

class VeWordProvider(GObject.GObject, GtkSource.CompletionProvider):
    # 继承CompletionProvider
    # 调用方式是 editor.props.completion 's provider add this provider.
    # 快捷键的调用顺序：
    # do_match
    # do_populate
    # do_get_priority
    #     
    # 调用顺序
    # do_match：判断是否匹配
    # do_get_interactive_delay：得到需要等待的时间，再显示
    # do_populate：加入匹配的候选项。
    # do_get_priority：设定此Provider提供的候选项目的等级。
    #   
    # 得到详细信息：
    # do_get_info_widget
    # do_get_icon：更新Provider的图标
    # do_get_name：更新Provider提供的名字。
    
    def __init__(self, prj):
        # prj:ModelProject:需要提供Completion支持的项目
        GObject.GObject.__init__(self)
        
        self.ide_prj = prj
        self.name = ""

    def do_get_name(self):
        # 返回Provider的名字，显示在弹出窗口的标题处。
        # return:str:名字，如果没有就返回None
        
        #print 'do_get_name'
        return self.name
    
    def do_get_icon(self):
        # 提供Provider的特殊标记。
        # return:GdkPixbuf.Pixbuf:如果没有就返回None
        
        #print 'do_get_icon'
        return None
        
    def do_get_activation(self):
        # 询问当前当前的Provider的类型。
        #return:GtkSource.CompletionActivation:类型。
        #    GtkSource.CompletionActivation.NONE:什么都不干。
        #    GtkSource.CompletionActivation.INTERACTIVE：当每次都insert进行。
        #    GtkSource.CompletionActivation.USER_REQUESTED:敲快捷键（比如ctrl+space)才出现。
        
        #print 'do_get_activation'
        return GtkSource.CompletionActivation.INTERACTIVE
    
    def do_get_interactive_delay(self):
        # 返回开始交互之前的时间（毫秒）
        # 输入过程中，如果停止一定的时间后，就会触发这个补全的动作。
        
        #print 'do_get_interactive_delay'
        return -1       # 使用缺省的设定
    
    def do_activate_proposal(self, proposal, ite):
        # 当选中了一个“替选”时，开发这可以选择自己处理，然后返回True，
        # 也可以什么都不做，返回False，系统执行缺省的方案。
        # 可以通过get_start_iter方法得到buffer中对应的match对象。
        # TODO:为什么在 do_match之前调用？
        
        #print 'do_activate_proposal'
        return False
    
    # 版本不同
    if os.getenv('GTKSOURCE_COMPLETION_PROVIDER') == "2.0":
        def do_get_start_iter(self, context, proposal):
            return False, None
    else:
        def do_get_start_iter(self, context, a, b):
            # 计算proposal的开始位置，设定的位置将在get_start_iter返回，用来在buffer中替换proposal。
            # 调用非常的频繁，不知道为什么
            # return:Bool, Gtk.TextIter:如果iter设置成了prosoal开始的位置，就返回True,否则就返回False。
        
            #print 'do_get_start_iter'
            return False, None
    
    def do_match(self, context):
        # 看看是否和当前的情况匹配，然后添加自己的Proposal。
        # context:GtkSource.CompletionContext:
        # return:Bool:True，如果匹配。
        # 如果返回True，会调用do_populate，
        # 返回False，什么都不调用。
        
        # 版本不同
        if os.getenv('GTKSOURCE_COMPLETION_PROVIDER') == "2.0":
            (isproposal, ite) = context.get_iter()
            if not isproposal:
                return False
        else:
            ite = context.get_iter()
        
        completion = context.props.completion
        view = completion.get_view()
        src_buf = view.get_buffer()
        word = self._get_word(src_buf, ite)
        
        # 空就不用检索了。
        if is_empty(word):
            return False
        
        #print 'do_match：', word
        self.name = word
    
        # 去查询是否有对应的补全单词
        self.completion_tags = self.ide_prj.get_completion_tags(word)
        if self.completion_tags is None or len(self.completion_tags) == 0:
            return False
        
        return True
    
    def do_populate(self, context):
        # 加入应该显示的proposal。

        #print 'do_populate'
        proposals = self._get_proposals()
        context.add_proposals(self, proposals, True)
    
    def do_get_priority(self):
        # 返回提供者的权限，这个决定了“候选”在弹出窗口中显示的先后顺序。
        # 等级越高，显示越在上面，0是缺省等级。
        
        #print 'do_get_priority'
        return 0
    
    def do_get_info_widget(self, proposal):
        # 显示定制的信息控件，显示这个候选项目的特殊信息。
        # 缺省使用Gtk.Label。如果自定义，必须实现do_update_info方法。
        # return:Gtk.Widget:如果没有特许需要，就返回None。
        
        #print 'do_get_info_widget'
        return None
    
    def do_update_info(self, proposal, info):
        # 如果do_get_info_widget内部实现特殊的控件，这里也必须实现。
        # 将Info的信息显示在get_info_widget的控件中。
        
        #print 'do_update_info'
        pass

    def _get_proposals(self):
        # 获得当前候选词语

        if self.completion_tags is None or len(self.completion_tags) == 0:
            return []
         
        names = []
        for tag in self.completion_tags:
            # label(str), text(str), icon(Pixbuf), info(str)
            ci = GtkSource.CompletionItem.new(tag.tag_name, tag.tag_name, None, "")
            names.append(ci)

        return names
        
    def _get_word(self, text_buf, ite):
        # 获取当前的单词。
        # gtk的控件是空格和_都是一个单词，而实际上编程应该是以空格为主。
        # text_buf:GtkSource.Buffer:编辑器的buffer
        # ite:Gtk.TextIter:当前光标所在的位置
        # return:string:单词
        
        # 在Gtk中，一个单词不是两边都是空格，有“_”也不行，所以这里修改单词取得的方法，
        # 变成自己去分析空格来完成。另外，包括在编辑器中双击鼠标，也必须是这个算法！

        word_start = ite.copy()

        # 得到以空格为区分的单词开头。
        while True:
            if word_start.starts_word():
                n = word_start.copy()
                # 获得前一个字符。
                if not n.backward_char():
                    break
                # 这里的算法应该有问题，如果判断为 空格，则不无法通过，不明白为什么？
                if text_buf.get_text(n, word_start, False) != "_":
                    break
            
            t = word_start.copy()
            t.backward_word_start()
            # 如果不进行无法移动的判断，会出现无穷循环问题，比如在“/*”后面敲“*”
            if word_start.equal(t):
                break
            else:
                word_start = t

        text = text_buf.get_text(word_start, ite, False)
        
        # TODO 不需要释放吗？但是如果释放的话，使用几次就崩溃。
        #word_start.free()
        #word_end.free()
        
        return text
    
# 需要注册这个对象到GObject中。
GObject.type_register(VeWordProvider)
