# -*- coding:utf-8 -*-

# 控制PlantUML工具。
# 本地必须有 plantuml.jar

import os, sys, subprocess, logging

class PlantUML(object):

    def __init__(self, jar_path):
        # @param jar_path:string: PlantUML's jar path.
        super(PlantUML, self).__init__()
        
        self.jar_path = jar_path
        if not os.path.isfile(jar_path):
            print "Cannot find PlantUML jar of \"%s\" in %s." % (jar_path, os.getcwd())
            sys.exit(1)

    def create_diagram(self, data_path, out_path):
        # @param data_path:string: data file path
        # @param out_path:string: output directory, not file
        # @return True: ok, False: failed.
        
        logging.debug("open %s" % data_path)
        f = open(data_path)
        for l in f:
            logging.debug(l)
        f.close()
        
        command = "java -jar %s %s -o %s -t png" % (self.jar_path, data_path, out_path)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE) 
        out, err = p.communicate()
        
        if err is not None:
            print err
            return False

        # show diagram
        data_file_name = os.path.basename(data_path)
        os.system('eog %s/%s.png' % (out_path, os.path.splitext(data_file_name)[0]))
