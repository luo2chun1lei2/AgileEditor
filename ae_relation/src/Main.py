#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys, logging, getopt, tempfile, shutil
from Element import *
from PlantUML import *

def util_print_frame():
    ''' 打印出现错误的位置的上一个调用点，用于调试。
    '''
    import inspect

    stack = inspect.stack()
    frame = stack[2][0]
    if "self" in frame.f_locals:
        the_class = str(frame.f_locals["self"].__module__)
    else:
        the_class = "Unknown"
    the_line = frame.f_lineno
    the_method = frame.f_code.co_name
    print "=-> %s:%d/%s" % (the_class, the_line, the_method)

def create_tmpfile(suffix):
    # 生成临时文件。
    fd, path = tempfile.mkstemp(suffix=(".%s" % suffix))
    return fd, path
        
def create_tmpdir():
    return tempfile.mkdtemp()

def test():
    e1 = AElementFactory.create_element('luocl')
    e2 = AElementFactory.create_relation('luocl')
    if e2 is None:
        e2 = AElementFactory.create_relation('luocl1')
    e2.attach_element(e1)
    e2.list_elements()
    e2.detach_element(e1)
    e2.list_elements()
    
    #planuml
    uml = PlantUML("../plantuml/plantuml.jar")
    data_fd, data_path = create_tmpfile("txt")
    os.write(data_fd, "@startuml\nAlice -> Bob: test\n@enduml")
    os.close(data_fd)
    
    out_dir = create_tmpdir()
    
    uml.create_diagram(data_path, out_dir)
    
    os.remove(data_path)
    shutil.rmtree(out_dir)
    

#######################################
## Entry of program.

def usage():
    print 'program usage:'
    print '-h, --help: show help information.'

def main(argv):
    u''' Analysis command's arguments '''
    
    # analysis code.
    try:
        opts, args = getopt.getopt(argv[1:], 'h', ['help'])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)
        
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit(0)
        else:
            print 'unknown arguments.'
            usage()
            sys.exit(2)
    
    test()
    
    sys.exit(0)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')
    
    main(sys.argv)
