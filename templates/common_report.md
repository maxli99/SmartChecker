SmartChecker检查结果
=========================

----------------------------------------

### 检查列表名称：   `{{checklist.filename}}`
###      检查log：   `{{logfile}}`
###     运行时间：   `{{timestamp}}`

------------------------------------------------------------
{% for r in results %}
###模块{{loop.index}} : {{r.name}}
###判断条件： 
```
{{r.criteria}}
```
###检查结果：`{{r.status}}`
###附加信息：
```
{{''.join(r.info)}}
```
------------------------------------------------------------
{% endfor %}


## There are total {{loop.length}} check modules executed.
{% for key,value in results.stats().items()%}
 * {{key}}: {{value}}
{%- endfor %}