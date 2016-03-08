FlexiNG TN Checker
========================

This script can be used to check the health status of FlexiNG according to the office Technical Notes.


# 检查模块开发指引

## 基本原理
检查模块在被调用时传入一个log文件的名称，然后运行run函数对log文件进行分析和判断，最后将结果填入status，info，error三个字段信息并返回给调用者。

## 开发指引
### 输入参数`logfile`
 logfile为log文件的文件名，包含绝对路径，如果不包含则到缺省目录log目录下查找。

### 返回参数 `ResultInfo`
 `ResultInfo`是一个包含检查结果的类。可以通过 `from libs.checker import ResultInfo`导入。它包含以下几个必选变量：

 * `status`， 检查结果状态，在`CheckStatus`中定义。比如：`PASSED`, `FAILED`, `UNKNOWN`等，详细情况请参阅 `CheckStatus`
 
 * `info`， 检查结果信息，是一个list列表或字符串，包含检查结果的相关数据或说明。
 
 * `error`，检查结果的错误信息，是一个list列表或字符串，包含检查过程中发生的错误信息。

### 调用入口 `run`函数

` run`函数是框架调用模块的入口，`logfile`为调用参数，传入log文件的文件名。

### 检查模块变量说明

* `module_id` 模块ID
   格式：TN-<发行者>-<编号>
  
  - 发行者为Global或China或Case
  - Global TN的编号就是TN本身的序号，China TN的编号为日期，Case的变化为CaseID

* `tag` 模块标签，一般为与检查模块相关的关键字，用于以后的分类和汇总

* `priority` 优先级

* `name` 模块名称

* `desc` 简要的描述

* `criteria` 判断依据

* `target_version` 适用软硬件版本

* `check_commands`  收集所需log信息的命令集合


