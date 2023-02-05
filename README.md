## RE:MockingBird 语音(真寻适配版)
基于在真寻插件库出现过的真寻版MockingBird制。

食用方法：把装了一堆py文件的文件夹丢进真寻插件目录即可。

本人作出的更改仅仅只有注释掉过期的`nonebot.export`方法以保障插件于2.0.0rc2的nonebot中能运作。

已测试能在Python3.10环境下正常运行,且可与nonebot_plugin_tts_gal插件共存。
测试环境如下：(win)
* 真寻bot: 1.6.6
* mockingbirdforuse: 0.2.3
* torch: 1.13.1
* numba: 0.56.4
* numpy: 1.23.5
* nonebot2: 2.0.0rc2

对于部分py3.10不能使用此插件的现象，本人猜测是包`mockingbirdforuse`的依赖信息陈旧导致：

用pip安装`numpy`及`torch`时，pip认为新版本`numpy`及`torch`不能满足`mockingbirdforuse`的要求，而py3.10中又不存在符合`mockingbirdforuse`所要求的旧版本`torch`，导致不能正常安装依赖环境。所以使用pip安装完后，如pip报错“pip不能正确处理`mockingbirdforuse`的依赖关系…”甚么的信息，请无视。

本人已更改原有的requirements.txt以符合此测试环境。

原README文件及使用说明见根目录下README.old.md。

原项目：https://github.com/AkashiCoin/nonebot_plugin_mockingbird