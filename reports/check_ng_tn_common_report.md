SmartChecker检查结果
=========================

----------------------------------------

### 检查列表名称：   `check_ng_tn.ckl`
###      检查log：   `log\test_All_NG_TN_check.log`
###     运行时间：   `2016-03-22 15:00`

------------------------------------------------------------

###模块1 : ngversion
###判断条件： 
```
Check if version number in ['3.1_1.0','3.2']
```
###检查结果：`PASSED`
###附加信息：
```
    - NG3.1_1.0_r235397_AB2
```
------------------------------------------------------------

###模块2 : Check PCC rule filter in disabled state
###判断条件： 
```
PCC rule filter in disabled state
```
###检查结果：`FAILED`
###附加信息：
```
Check failed.
```
------------------------------------------------------------

###模块3 : FlexiNG(NG3.x) AS/SAB Memory leak Check
###判断条件： 
```
正常的内存利益率: AS < 110MB or SAB < 500MB

解决方案：
  1. 有条件关闭 hicut 的项目就关闭（因为关闭 hitcut 会导致 Node 负荷小幅增加，需要提前检查 CPU 使用情况）。
  2. 没有条件关 hitcut 的项目，必需要把检查内存利用率的操作列入日常的维护计划

```
###检查结果：`PASSED`
###附加信息：
```
    - AS5-0 memory: 99.300994873
    - AS5-0 memory: 0.678421020508
    - AS5-0 memory: 19.6645202637
    - AS5-0 memory: 11.9645233154
    - AS5-1 memory: 26.8623962402
    - AS5-1 memory: 42.6815185547
    - AS6-0 memory: 26.8623962402
    - AS6-0 memory: 42.6815185547
    - AS6-1 memory: 26.8623962402
    - AS6-1 memory: 42.6815185547
    - AS11-0 memory: 26.8674926758
    - AS11-0 memory: 42.6824645996
    - AS11-1 memory: 46.965713501
    - AS11-1 memory: 62.756439209
    - SAB2-1 memory: 62.756439209
    - SAB2-0 memory: 158.12387085
    - SAB2-0 has a max memory 158.12 MB
    - AS5-0 has a max memory 99.300 MB

```
------------------------------------------------------------

###模块4 : 校验Session Profile中的Charging character配置
###判断条件： 
```
NG Charging character configuration have problem 
```
###检查结果：`FAILED`
###附加信息：
```
- NG version: 3.1_1.0 (in target_version list). 
cmnet-session-profile have NOT charchar-index=0 
cmnetlte-session-profile have NOT charchar-index=0 
cmwaplte-session-profile have NOT charchar-index=0 
cmwap-session-profile have NOT charchar-index=0 

```
------------------------------------------------------------



## There are total 4 check modules executed.

 * FAILED: 2
 * PASSED: 2