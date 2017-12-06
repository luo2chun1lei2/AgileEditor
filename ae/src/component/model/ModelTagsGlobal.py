# -*- coding:utf-8 -*-

''' 操纵Tag相关的处理。
整体分析采用Global（gtags）来实现，而文件内部则准备使用idutils来实现。

Global的问题:
1, 只能有一个代码目录，所以必须将代码集中在一起。
2, 不能指定Tags等文件所在的目录，所以Tags文件必须在代码目录的开始。
3, 使用ctag来更加详细的管理tag。
'''

# ctags的type
# C
#     c  classes
#     d  macro definitions
#     e  enumerators (values inside an enumeration)
#     f  function definitions
#     g  enumeration names
#     l  local variables [off]
#     m  class, struct, and union members
#     n  namespaces
#     p  function prototypes
#     s  structure names
#     t  typedefs
#     u  union names
#     v  variable definitions
#     x  external and forward variable declarations [off]
# C++
#     c  classes
#     d  macro definitions
#     e  enumerators (values inside an enumeration)
#     f  function definitions
#     g  enumeration names
#     l  local variables [off]
#     m  class, struct, and union members
#     n  namespaces
#     p  function prototypes
#     s  structure names
#     t  typedefs
#     u  union names
#     v  variable definitions
#     x  external and forward variable declarations [off]

import os, subprocess, re, logging
from framework.FwUtils import *
from framework.FwComponent import FwComponent
from ModelTag import ModelTag

class GtProcess(object):
    ''' 仅限此文件内使用。 
    TODO 后台更新的进程，和其他的global不一样，是同步完成的，能不能改成异步的？
    '''

    def __init__(self, work_dir):
        # 建立进行实例，注册回调事件。
        # wdir:string:工作目录。

        # work_dir:string:命令的工作目录。
        self.work_dir = work_dir

    def run_rebuild_process(self, pargs, cmd_env):
        # 运行重建进程。
        # pargs:[string]:命令和参数列表。
        # cmd_env:Map<string, string>:命令的环境变量定义

        p_cmd = ' '.join(pargs)
        # TODO: 不能使用 “ env=cmd_env,”，会导致$HOME/.globalrc不起作用，奇怪？
        p = subprocess.Popen(p_cmd, shell=True, cwd=self.work_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()

class ModelTagsGlobal(FwComponent):
    ''' 使用GNU Global工具来分析代码，生成Tags文件。
    '''

    # 命令的环境变量：
    # TODO: GTAGSLIBPATH 是 global命令支持设定GTAGS联合查询，但是可能需要在项目管理上，可以设定相关性。
    #         需要修改：参考库的路径是固定的，另外如何设定相关性。
    cmd_env = {'GTAGSLIBPATH':'/home/luocl/workshop/src/emu/soter/'}

    def __init__(self):
        # 初始化

        super(ModelTagsGlobal, self).__init__()
        # project:ModelProject:项目对象。
        self.project = None

    # override component
    def onRegistered(self, manager):
        info = [{'name':'model.tags.update', 'help':'update the tags on the newest state.'},
                {'name':'model.tags.find_defination', 'help':'find the defination.'},
                {'name':'model.tags.find_reference', 'help':'find the reference.'},
                {'name':'model.tags.find_symbol_in_project', 'help':'find the symbol in project.'},
                {'name':'model.tags.find_symbol_in_file', 'help':'find the reference.'},
                {'name':'model.tags.find_file', 'help':'find the file by pattern.'},
                {'name':'model.tags.find_symbol_with_prefix_in_project', 'help':'find the symbol with prefix in project.'},
                ]
        manager.register_service(info, self)

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "model.tags.update":
            self.project = params['project']  # ModelProject
            self.prepare()
            return (True, None)
        elif serviceName == "model.tags.find_defination":
            return (True, {'results':self.query_defination_tags(params['text'])})  # [ModelTag]
        elif serviceName == "model.tags.find_reference":
            return (True, {'results':self.query_reference_tags(params['text'])})  # [ModelTag]
        elif serviceName == "model.tags.find_symbol_in_project":
            return (True, {'results':self.query_grep_tags(params['text'], params['ignore_case'])})  # [ModelTag]
        elif serviceName == "model.tags.find_symbol_in_file":
            return (True, {'results':self.query_ctags_of_file(params['path'])})  # [ModelTag]
        elif serviceName == "model.tags.find_file":
            return (True, {'results':self.query_grep_filepath(params['text'], params['ignore_case'])})  # [ModelTag]
        elif serviceName == "model.tags.find_symbol_with_prefix_in_project":
            return (True, {'results':self.query_prefix_tags(params['text'])})  # [ModelTag]
        else:
            return False, None

    def _get_tags_path(self):
        # 返回Tags文件应该在的目录
        # return:string:也可能时空。

        if len(self.project.src_dirs) > 0:
            return self.project.src_dirs[0]
        else:
            return None

    def _has_tags(self):
        # 判断是否有Tags文件。
        # return:Bool:
        path = self._get_tags_path()
        f = os.path.join(path, 'GTAGS')
        return os.path.exists(f)

    def prepare(self):
        # 如果Tags已经存在了，就更新，否则生成。
        path = self._get_tags_path()
        if self._has_tags():
            self._rebuild()
        else:
            self._build()

    def _build(self):
        # 生成对应的Tags
        try:
            # 将obj/目录排斥在外部，在~/.globalrc中定义。
            pargs = [ 'gtags', '' ]  # 没有使用IdUtils
            gtp = GtProcess(self.project.src_dirs[0])
            gtp.run_rebuild_process(pargs, self.cmd_env)
        except ValueError as err:
            logging.error("ValueError: %s" % err)
            # return None, None
        except IOError as err:
            logging.error("IOError: %s" % err)

    def _rebuild(self):
        # 如果文件更新了，就重新更新Tags。
        pargs = [ 'global', '-u' ]

        gtp = GtProcess(self.project.src_dirs[0])
        gtp.run_rebuild_process(pargs, self.cmd_env)

    def _parse_file_tags_result(self, text):
        # 分析文件内部的Tag的结果
        # 格式 “文件路径 标记 行数 所在行的内容”
        text = re.split('\r?\n', text)

        res = []
        for line in text:
            if line == '':
                continue
            line = line.split(' ', 3)
            tag = ModelTag(name=line[1], file_path=line[0], line_no=int(line[2]), content=line[3])
            res.append(tag)

        return res

    def _parse_completion_tags_result(self, text):
        # 分析单词补全Tag的结果
        # 格式 “名字”

        text = re.split('\r?\n', text)
        res = []
        for line in text:
            if line == '':
                continue
            tag = ModelTag(name=line)
            res.append(tag)

        return res

    def query_defination_tags(self, name):
        # 查询指定的名字在哪里定义

        # cscope的模式：file_path tag_name line_no line_content
        # -a:查询结果是绝对路径
        p_cmd = 'global -a --result cscope ' + name
        wsdir = self.project.src_dirs[0]
        logging.debug('cmd:%s, cwd:%s' % (p_cmd, wsdir))
        p = subprocess.Popen(p_cmd, shell=True, cwd=wsdir, env=self.cmd_env,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        (stdoutput, erroutput) = p.communicate()

        return self._parse_defination_tags_result(stdoutput)

    def _parse_defination_tags_result(self, text):
        # 分析名字Tag的查询结果。
        return self._parse_file_tags_result(text)

    def query_reference_tags(self, name):
        # 查询指定的名字在哪里被使用

        # cscope的模式：file_path tag_name line_no line_content
        # -a:查询结果是绝对路径, -r:引用
        p_cmd = 'global -a -r --result cscope ' + name
        wsdir = self.project.src_dirs[0]
        logging.debug('cmd:%s, cwd:%s' % (p_cmd, wsdir))
        p = subprocess.Popen(p_cmd, shell=True, cwd=wsdir, env=self.cmd_env,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        (stdoutput, erroutput) = p.communicate()

        return self._parse_reference_tags_result(stdoutput)

    def _parse_reference_tags_result(self, text):
        # 分析名字Tag的查询结果。
        return self._parse_file_tags_result(text)

    def query_prefix_tags(self, prefix):
        # 根据前缀，得到Tags名字。
        # cscope的模式：file_path tag_name line_no line_content
        # -a:查询结果是绝对路径, -r:引用，-c [前缀]:查询补全的单词
        p_cmd = 'global -a --result cscope -c ' + prefix
        wsdir = self.project.src_dirs[0]
        logging.debug('cmd:%s, cwd:%s' % (p_cmd, wsdir))
        p = subprocess.Popen(p_cmd, shell=True, cwd=wsdir, env=self.cmd_env,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        (stdoutput, erroutput) = p.communicate()

        return self._parse_completion_tags_result(stdoutput)

    def query_grep_tags(self, pattern, ignoreCase=False):
        # 根据模式在项目中查找，ignoreCase是否忽略大小写
        # cscope的模式：file_path tag_name line_no line_content
        # -g:按照模式查找，-i:忽略大小写
        p_cmd = 'global -a --result cscope -g \'' + pattern + '\''
        if ignoreCase:
            p_cmd = p_cmd + ' -i'
        wsdir = self.project.src_dirs[0]
        logging.debug('cmd:%s, cwd:%s' % (p_cmd, wsdir))
        p = subprocess.Popen(p_cmd, shell=True, cwd=wsdir, env=self.cmd_env,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        (stdoutput, erroutput) = p.communicate()

        return self._parse_file_tags_result(stdoutput)

    def query_grep_filepath(self, pattern, ignoreCase=False):
        # 根据模式在文件路径找查找，ignoreCase是否忽略大小写
        # cscope的模式：file_path tag_name line_no line_content
        # -P:检索文件路径，-i:忽略大小写
        p_cmd = 'global -a --result cscope -P \'' + pattern + '\''
        if ignoreCase:
            p_cmd = p_cmd + ' -i'

        wsdir = self.project.src_dirs[0]
        logging.debug('cmd:%s, cwd:%s' % (p_cmd, wsdir))
        p = subprocess.Popen(p_cmd, shell=True, cwd=wsdir, env=self.cmd_env,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        (stdoutput, erroutput) = p.communicate()

        return self._parse_file_tags_result(stdoutput)

    def query_ctags_of_file(self, file_path):
        # 查询指定文件的cTags:
        # return:[string]:Tag列表。

        # 命令 ctags --fields=+n --excmd=number --sort=no -f - b.c
        # --fields=+n 表示查询什么模式，+表示加入，-表示不要
        # a   Access (or export) of class members
        # f   File-restricted scoping [enabled]
        # i   Inheritance information
        # k   Kind of tag as a single letter [enabled]
        # K   Kind of tag as full name
        # l   Language of source file containing tag
        # m   Implementation information
        # n   Line number of tag definition
        # s   Scope of tag definition [enabled]
        # S   Signature of routine (e.g. prototype or parameter list)
        # z   Include the "kind:" key in kind field
        # t   Type and name of a variable or typedef as "typeref:" field [enabled]
        # --sort=no 不排序
        # -f - 输出结果放到标准输出中

        # --extra=[+|-]flags
        # f   Include an entry for the base file name of every source file (e.g.  "example.c"), which addresses the first line of
        #     the file.
        # q   Include an extra class-qualified tag entry for each tag which is a member of a class (for languages for which  this
        #     information  is  extracted; currently C++, Eiffel, and Java). The actual form of the qualified tag depends upon the
        #     language from which the tag was derived (using a form that is most natural for how qualified calls are specified in
        #     the  language).  For C++, it is in the form "class::member"; for Eiffel and Java, it is in the form "class.member".
        #     This may allow easier location of a specific tags when multiple occurrences of a tag name occur in  the  tag  file.
        #     Note, however, that this could potentially more than double the size of the tag file.

        # 显示的结果，每行中用“\t”来分割
        # TElement    /home/luocl/myproject/think2/src/element.h    30;"    function    line:30    class:TElement

        p_cmd = ' ctags --fields=+n+K --excmd=number --sort=no -f - ' + file_path
        wsdir = self.project.src_dirs[0]
        logging.debug('cmd:%s, cwd:%s' % (p_cmd, wsdir))
        p = subprocess.Popen(p_cmd, shell=True, cwd=wsdir, env=self.cmd_env,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        (stdoutput, erroutput) = p.communicate()

        return self._parse_ctags_of_file(stdoutput)

    def _parse_ctags_of_file(self, text):
        # 分析文件内部的Tag的结果
        # 格式 “文件路径 标记 行数 所在行的内容”
        text = re.split('\r?\n', text)

        res = []
        for line in text:
            if line == '':
                continue
            frags = line.split('\t')

            if len(frags) >= 5:
                line_no = frags[4].split(":", 2)[1]
            else:
                line_no = ""

            if len(frags) >= 6:
                tag_scope = frags[5].split(":", 2)[1]
            else:
                tag_scope = ""

            tag = ModelTag(name=frags[0],
                           file_path=frags[1],
                           line_no=int(line_no),
                           content="",
                           tag_type=frags[3],
                           tag_scope=tag_scope
                           )
            res.append(tag)

        return res
