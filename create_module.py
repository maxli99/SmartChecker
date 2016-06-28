#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""This tool used to create the check module for SmartChecker.

Usage:
   create_module.py <module_info> [-t template.py]

Description:
   The <module_info> is a YAML file which define the module info. it should 
   include below fields:

    module_name: 
    module_path: 
    ne_type:     
    description: 
    name:                
    module_id:     
    priority:      
    target_version:
    tags:          
    criteria: 
"""
import sys,os
import argparse
import yaml,logging
import setsitenv
from libs.reportor import JinjaTemplate
from libs.tools import MessageBuffer

M_TEMPLATE = "module_template.py"

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',)
def parse_args():
    parser = argparse.ArgumentParser()
    parser.usage = __doc__
    parser.add_argument("module_info",action="store",help="The YAML file define the detail info of module")
    parser.add_argument('-t','--template',default=M_TEMPLATE, help="specify the template file")

    args = parser.parse_args()

    return args

def generate_file(moduleinfo,template_file):
    tmpl = JinjaTemplate("modules/")
    tmpl.load(filename=template_file)

    return tmpl.render(**moduleinfo)

if __name__ == "__main__":
    args = parse_args()
    tmplbuf = MessageBuffer()

    _info = yaml.load(file(args.module_info))
    output_file = os.path.join(_info['module_path'],_info['module_name'])
    module_file = generate_file(_info,args.template)

    tmplbuf.append(module_file)
    try:
        tmplbuf.write(output_file)
    except Exception as e:
        logging.info("FAILED when save to file:%s\n%s" % (output_file,e))
        exit(1)
    print "Save the new module file to %s" % output_file