Release Note
====================
* v0.800, 2016/3/13
  
  + 模块支持中文字符。
  + 增加以下目录：
  
    - templates 用于存放用于报告和显示的jiaja模板文件
    - reports   用于存放生成的检查报告
    
  + checklist文件内容格式变更，增加`templates`，`paths`等变量。原`modules`变量变更为`modules_name`.
    详情请参阅`example.ckl`
    
* v0.613, 2016/3/2

  + 增加以下目录：
    
    - test  用于存放测试用的模块或程序
    - TN    存放检查模块对应的TN文件
    - docs  存放项目相关文档
    
  + 增加公共模块`LogSpliter`，该工具能从整段MME的log中截取某一条命令的输出结果。
  + 检查模块增加一个可选list变量：check_commands，该变量包含收集模块所需要的信息的命令。
变量格式：
````
    check_commands = [
        (<command1>, <command1 description>),
        (<command2>, <command2 description>),
        ......
		]
````    
  
  + 命令行show（-s）命令增加输出检查模块check_commands列表中内容的功能。可以用于生成收集log信息
    的命令集
    
    *Example：*
    
	    D:\Smartchecker>python smartchecker.py -s checklist\ns_fragment.ckl
        - name: Check the FNS software version
          desc: Analysis and Check the FlexiNS software version.


        - name: Verify the Disk fragmentation problem in FNS
          desc: Check the NTP setting for the 2015 leap second issue
        In case of systems having AMPP1 -A blades, a critical bug was found in kernel that may cause
        a deadlock to occur when NTP leap second is applied to the system. If the fault should occur
        the system will restart itself (via watchdog functionality) thus causing a service break.

        There are total 2 check modules need to been run.

	    ####################################################################
        # Below are all the commands used to collect the needed information:
        ####################################################################
        ## Show the ns packages information
        ZWQO:CR;

        ## Show omu harddisk info
        ZDDE:OMU:"ZMA:W0,F3,,,,,","ZMA:W1,F3,,,,,","ZGSC:,00FC";

        ## Show mchu harddisk info
        ZDDE:MCHU:"ZMA:W0,F3,,,,,","ZMA:W1,F3,,,,,","ZGSC:,00FC";