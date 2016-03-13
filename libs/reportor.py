# -*- coding: utf-8 -*-

import re,os
from jinja2 import Environment, FileSystemLoader,Template
from jinja2.exceptions import TemplateNotFound


class JinjaTemplate(object):
    """A generator of Jinja Template
Usage:
    jinja = JinjiaTemplate()
    temp = jinja.template('template_name')
    tmpl.render()
    """
    def __init__(self,path='./'):
        self.template_path = path
        self.loader = FileSystemLoader(path)
        self.extensions = ['jinja2.ext.do']
        self.env=Environment(loader=self.loader,
                             extensions=self.extensions)
        
    def template(self,filename=None):
        if filename:
            return self.env.get_template(filename)
        else:
            return Template
    
    def setenv(self, loader='',ext=[]):
        loader = loader or self.loader
        ext = ext or self.extensions
        self.env=Environment(loader=loader,externsions=ext)
    
    
class CheckReport(object):
    """Class generate report with multi formats.
 supported formats:
    md,     markdown
    html,   html
    
    """
    def __init__(self,template_path='templates/'):
        self.config = {}
        self.template_name =''
        self.data = {}
        self.report = None
        self.template_path = template_path

        self.env = Environment(loader=FileSystemLoader(self.template_path))
        
    def load_data(self):
        """excute the getdata functions from reportConfig
        """
        pass
        
    def generate(self):
        """Generate the report 
        """
        template_name = 'template_name'
        output_path = output_path or self.config.output_path
        report = ''
        
        #print "template:",template_name

        #print "%s/%s" % (template_env.loader.searchpath[0],template_name)
        try:
            tmpl = template_env.get_template(template_name)
        except TemplateNotFound,e:
            msg = "template: %s not found." % e
            return False, msg
         
        #print "render data:", self.data 
        report = tmpl.render(**self.data)
        result = True
        self.report = report
        
        return report
        
    def save(self,output_path=''):
        filename=output_path + self.report_name
        self.filename = filename
        with open(filename,'wb') as fp:
            fp.write(self.report.encode('utf8'))


if __name__ == "__main__":
    rpt = Reportor()
    rpt.generate()
    