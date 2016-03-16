## 基本原理
检查模块在被调用时传入一个log文件的名称，然后运行run函数对log文件进行分析和判断，最后将结果填入status，info，error三个字段信息并返回给调用者。

## 开发指引
### 输入参数`logfile`
 logfile为log文件的文件名，包含绝对路径，如果不包含则到缺省目录log目录下查找。

### 返回参数 `ResultInfo`
 `ResultInfo`是一个包含检查结果的类。可以通过 `from libs.checker import ResultInfo`导入。它包含以下几个必选变量：

 * `status`， 检查结果状态，在`CheckStatus`中定义。比如：`PASSED`, `FAILED`, `UNKNOWN`等，详细情况请参阅 `libs/checker.py`程序里的`CheckStatus` 类
 
 * `info`， 检查结果信息，是一个list列表或字符串，包含检查结果的相关数据或说明。
 
 * `error`，检查结果的错误信息，是一个list列表或字符串，包含检查过程中发生的错误信息。

 > 注： 以上`info` 和`error`变量的内容可以使用中文。使用中文字符时，请记得在字符串前加unicode的标志符 `u`。

### 调用入口 `run`函数

 `run`函数是框架调用模块的入口，`logfile`为调用参数，传入log文件的文件名。

### 检查模块变量说明

* `module_id` 模块ID

   格式：TN_<发行者>_<编号>
  
  - 发行者为Global或China或Case
  - Global TN的编号就是TN本身的序号，China TN的编号为日期(10位)，Case的编号为CaseID

    **例子：**
    
    > TN_China_2015101300         
  
* `tag` 模块标签，一般为与检查模块相关的关键字，用于以后的分类和汇总

* `priority` 优先级。 为TN或case的优先级

* `name` 模块名称

* `desc` 简要的描述

* `criteria` 判断依据说明。可以使用中文字符描述。

* `target_version` 适用软件版本。此变量为一List列表，列表里包含适用__软件版本__的具体版本号。软件版本号可参考文档“FlexiNS及FlexiNG版本信息列表”

* `check_commands`  收集所需log信息的命令集合。例子如下：

     check_commands = [
	("ZWOI:;","show the NS data of the parameters defined in the PRFILE"),
	("ZWQO:CR;","show the NS packages information"),
	("ZKAL:;","show the NS cause code set names")
     ]

### 其他

 * 模块编写和测试完毕后，在commit到Github之前，请同时把一小段用于测试的log文件置于项目的/log目录下，命名方式为：
`test_模块名称_附加信息.log`.