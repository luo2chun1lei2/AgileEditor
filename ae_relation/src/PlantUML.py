# -*- coding:utf-8 -*-

'''
控制PlantUML工具的
'''

import os, sys, subprocess


class PlantUML(object):

    def __init__(self, jar_path):
        # @param jar_path:string: PlantUML's jar path.
        super(PlantUML, self).__init__()
        
        self.jar_path = jar_path
        if not os.path.isfile(jar_path):
            print "Cannot find PlantUML jar of \"%s\" in %s." % (jar_path, os.getcwd())
            sys.exit(1)
            
    def create_diagram(self, data_path, out_dir_path):
        # @param data_path:string: data file path
        # @param out_dir_path:string: output directory, not file
        # @return True: ok, False: failed.
        
        print "=== %s ===" % data_path
        f = open(data_path)
        for l in f:
            print l
        f.close()
        
        command = "java -jar %s %s -o %s -t png" % (self.jar_path, data_path, out_dir_path)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE) 
        out, err = p.communicate()
        
        if err is not None:
            print err
            return False
         
        # for line in out.splitlines():
        #    print line

        # show png
        data_file_name = os.path.basename(data_path)
        os.system('eog %s/%s.png' % (out_dir_path, os.path.splitext(data_file_name)[0]))
