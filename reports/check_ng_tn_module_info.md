check_ng_tn检查列表模块信息
====================================

--------------------------------------------------

### 检查列表包含以下模块：



####Module  #1

#### 1.模块名称: ngversion

#### 2.判断条件:
```
Check if version number in ['3.1_1.0','3.2']
```
 
#### 3.说明:

  FlexiNG Version Checking
  Check the NG version, passed if version >= 3.1


---------------

####Module  #2

#### 1.模块名称: Check PCC rule filter in disabled state

#### 2.判断条件:
```
PCC rule filter in disabled state
```
 
#### 3.说明:

  中Check the PCC rule filter in "disabled" state

VALIDITY: NG3.2, NG15

Correction for this issue will be provided in NG15 MP1 and NG3.2 3.0

SOLUTION:
Use fsclish command unset to completely remove unwanted filters from pcc-rule configuration and do not use filters in disabled state.


---------------

####Module  #3

#### 1.模块名称: FlexiNG(NG3.x) AS/SAB Memory leak Check

#### 2.判断条件:
```
正常的内存利益率: AS < 110MB or SAB < 500MB

解决方案：
  1. 有条件关闭 hicut 的项目就关闭（因为关闭 hitcut 会导致 Node 负荷小幅增加，需要提前检查 CPU 使用情况）。
  2. 没有条件关 hitcut 的项目，必需要把检查内存利用率的操作列入日常的维护计划

```
 
#### 3.说明:

  由于有NG3.x 版本SAEGW的AS/SAB存在内存泄露的问题，导致发生终端用户上网困难等多种症状非常多样，
需要对SAE经常检查内存是否泄露。


---------------

####Module  #4

#### 1.模块名称: 校验Session Profile中的Charging character配置

#### 2.判断条件:
```
NG Charging character configuration have problem 
```
 
#### 3.说明:

  检查Charging character配置（华为PCRF和CC=0用户问题）
开启gx 功能后，用户签约为CC=0 的用户GX CCR 消息中的携带的online（在线计费）和
offline（离线计费）被设置为disable 状态（不计费），由PCRF 来指示计费方式。华为PCRF 会返回与SAEGW 发送一致的online（在线计费）
和 offline（离线计费）字段，disable 状态（不计费），导致CC=0 的用户不产生话单。
添加下面的配置即可避免上述的问题。
charchar-index = 0
charging-profile = charging-profile-1
建议将其余字段均使用缺省的计费方式。
When enable gx function, subscriber with CC=0 's GX CCR message will set th online and 
offline as disable and the charging mode decide by PCRF . But Huawei PCRF will return 
disable , so these subsciber(CC=0) will not generate CDR.
You can add the followed config to resolve the problem:
charchar-index = 0
charging-profile = charging-profile-1
other cc=1,2,3,5,6,7,9 can use the same way.


---------------



### 请运行以下命令收集检查所需的信息

**注意：**

> 以下有部分命令仍缺部分参数，请根据实际网元情况填写相关的网元名称。 

-------------------------------------------------------------------------
```
#show the FNG version information
fsclish -c "show ng version" 

### show service-awareness pcc-rule
show ng service-awareness pcc-rule *

### show the {{apn_name}} session profiles
show ng session-profile {{apn_name}}-session-profile

```
