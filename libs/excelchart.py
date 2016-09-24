# -*- coding: utf-8 -*-
from openpyxl.chart import BarChart, LineChart, PieChart 
from openpyxl.chart import Series, Reference

class Chart(object):
    """Abstract Class for Excel Chart
    """
    def __init__(self,chartinfo=None):
        if chartinfo:
            self.load_setting(chartinfo)

    def add_to_sheet(self,sheet):
        sheet.add_chart(self.chart,self.location)

    def add_data(self,data):
        self.chart.add_data(data)

    def set(self,**kwargs):
        for key,value in kwargs:
            setattr(self.chart,key,value)

    def load_setting(self,chartinfo):
        setting = chartinfo.get('setting',{})
        for key,value in chartinfo.items():
            setattr(self.chart,key,value)

class ExcelBarChart(Chart):
    def __init__(self,chartinfo=None):
        self.chart = BarChart()
        super(ExcelBarChart,self).__init__(chartinfo)
    
    def load_setting(self,chartinfo):
        self.chart.title = chartinfo.get('name',"Chart")
        self.location = 'B15'
        setting = chartinfo['setting']
        super(ExcelBarChart,self).load_setting(setting)


class ExcelLineChart(Chart):
    def __init__(self,chartinfo=None):
        self.chart = LineChart()
        super(ExcelLineChart,self).__init__(chartinfo)
    
    def load_setting(self,chartinfo):
        self.chart.title = chartinfo.get('name',"LineChart")

class ExcelPieChart(Chart):
    def __init__(self,chartinfo=None):
        self.chart = PieChart()
        super(ExcelPieChart,self).__init__(chartinfo)
    
    def load_setting(self,chartinfo):
        self.chart.title = chartinfo.get('name',"PieChart")

class ChartFactory(object):
    """Class present the chart object in Excel
    """
    SUPPORTED_CHART = {
        'BarChart' : ExcelBarChart,
        'PieChart' : ExcelPieChart,
        'LineChart': ExcelLineChart,
    }

    def create_chart(self,chartinfo):
        chart_type = chartinfo.get('type',None)
        chart_class = self.SUPPORTED_CHART.get(chart_type,ExcelLineChart)
        print chartinfo
        chart = chart_class(chartinfo)
        print chart.chart
        print chart.chart.type

        return chart
