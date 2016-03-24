SmartChecker检查结果
=========================

----------------------------------------

### 检查列表名称：   `check_ng_tn.ckl`
###      检查log：   `log\filter_in_disable_state.log`
###     运行时间：   `2016-03-23 11:52`

------------------------------------------------------------

### There are total 5 check modules executed.

 * UNKNOWN: 3
 * PASSED: 1
 * FAILED: 1

------------------------------------------------------------

###模块1 : FlexiNG basic info collecting
###判断条件： 
```
FNG basic info collecting.
```
###检查结果：`PASSED`
###附加信息：
```
FlexiNG Info:
 - hostname: 
 -  version: None
 - hardware: 

```
------------------------------------------------------------

###模块2 : ngversion
###判断条件： 
```
Check if version number in ['3.1_1.0','3.2']
```
###检查结果：`UNKNOWN`
###附加信息：
```
unknow version
```
------------------------------------------------------------

###模块3 : Check PCC rule filter in disabled state
###判断条件： 
```
PCC rule filter in disabled state
```
###检查结果：`FAILED`
###附加信息：
```
Rule Name: WAP_ZYYY
filter = ZYYY2                             precedence = 1040  filter-state = disabled
filter = ZYYY3                             precedence = 1060  filter-state = enable

```
------------------------------------------------------------

###模块4 : FlexiNG(NG3.x) AS/SAB Memory leak Check
###判断条件： 
```
正常的内存利益率: AS < 110MB or SAB < 500MB

解决方案：
  1. 有条件关闭 hicut 的项目就关闭（因为关闭 hitcut 会导致 Node 负荷小幅增加，需要提前检查 CPU 使用情况）。
  2. 没有条件关 hitcut 的项目，必需要把检查内存利用率的操作列入日常的维护计划

```
###检查结果：`UNKNOWN`
###附加信息：
```
    - NG version can't be determindated.
    - Can't found the memory usage info.

```
------------------------------------------------------------

###模块5 : 校验Session Profile中的Charging character配置
###判断条件： 
```
NG Charging character configuration have problem 
```
###检查结果：`UNKNOWN`
###附加信息：
```
- NG version can't be determindated. 

```
------------------------------------------------------------


