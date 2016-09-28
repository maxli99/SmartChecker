# -*- coding: utf-8 -*-
"""This module handle the Report
"""
import re
import os
import codecs
from jinja2 import Environment, FileSystemLoader,Template
from jinja2.exceptions import TemplateNotFound
from jinja2._compat import string_types
from excelreport import ExcelReport, Table
from messagelogger import MessageLogger

logger=MessageLogger('reportor')

class JinjaTemplate(object):
    """A generator of Jinja Template
  Usage:
    tmpl = JinjiaTemplate()
    tmpl.load(filename=template_filename)
    tmpl.load('template_str')
    tmpl.render()
    """
    def __init__(self,path='./', filename=None):
        self.template_path = path
        self.loader = FileSystemLoader(path)
        self.extensions = ['jinja2.ext.do']
        self.env=Environment(loader=self.loader,
                             extensions=self.extensions)
        
        if filename:
            self.load(filename=filename)

    def load(self,template_string=None,filename=None):
        if filename:
            self.template = self.env.get_template(filename)
        elif template_string:
            self.template = Template(template_string)
        else:
            self.template = Template('')
            
        return self.template
        
    def setenv(self, loader='',ext=[]):
        loader = loader or self.loader
        ext = ext or self.extensions
        self.env=Environment(loader=loader,externsions=ext)
    
    def render(self, **kwargs):
        return self.template.render(**kwargs)

    def stream(self,**kwargs):
        return self.template.stream(**kwargs)

class VariableDict(dict):
    """A class store the variables for report template"""
    def add(self,**kwargs):
        self.update(kwargs)

    def remove(self,key):
        self.pop(key)

class HTMLReportBuilder(object):
    """A builder for HTML report
    """
    def __init__(self, filename=None,path='./'):
        self.template_path = path
        self.template_name = filename

        self.template = JinjaTemplate(path=path)
        if filename:
            self.template.load(filename=filename)

    def fill_data(self,**kwargs):
        self.stream = self.template.render(**kwargs)
        logger.debug("HTMLReportBuilder.stream: %s, %s" % (type(self.stream),len(self.stream)))

    def save(self,filename):
        with codecs.open(filename,'wb','utf-8') as fp:
            fp.write(self.stream)
        


class ExcelReportBuilder(object):
    """A builder for Excel report"""
    pass

class MarkdownReportBuilder(object):
    """A builder for Marddown report"""
    pass

class CheckReport(object):
    """Class generate report with multi formats.
 supported formats:
    md,     markdown
    html,   html
    
    """
    def __init__(self,
                 template_path='templates/',
                 template_name=None,
                 builder=None,
                 output_path='',):

        self.config = {}
        self.data = {}
        self.template_path = template_path
        self.template_name = template_name
        self.output_filename = "report.%s"
        self.output_path = output_path

        self.builder = builder        
    
    def get_builder(self,_type):
        self.builder = get_builder(_type, path=self.template_path, filename=self.template_name)

    def fill_data(self, **kwargs):
        self.add_data(**kwargs)
        self.builder.fill_data(**self.data)
        
    def save(self,filename=None):
        _filename = filename or self.output_filename
        saved_filename = os.path.join(self.output_path,_filename)
        try:
            self.builder.save(saved_filename)
        except Exception as err:
            return None

        return saved_filename

    def add_data(self,**kwargs):
        self.data.update(kwargs)

    def get_data(self,key):
        return self.data.get(key)
        
    def remove_data(self,key):
        self.data.pop(key)

def get_builder(builder_type,**kwargs):
    """return the report builder according the builder type

    'html'   HTMLReportBuilder
    'xlsx'   ExcelReportBuilder
    'xls'    ExcelReportBuilder
    """
    builders = {'html': HTMLReportBuilder,
                'xlsx': ExcelReportBuilder,
                'xls' : ExcelReportBuilder,
                'md'  : MarkdownReportBuilder,
                }

    builder = builders.get(builder_type,HTMLReportBuilder)
    return builder(**kwargs)

if __name__ == "__main__":
    report = CheckReport()
    results = {}
    report.add_data(results=results)
    report.get_builder('html')
    