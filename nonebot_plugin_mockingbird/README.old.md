## MockingBird 语音(真寻适配版)

此项目灵感来源于 [Diaosi1111/nonebot_mockingbird_plugin](https://github.com/Diaosi1111/nonebot_mockingbird_plugin)

### 食用方法

1. 首先使用命令安装mockingbirdonlyforuse:

``` 
pip install mockingbirdforuse
```

**如有报错请为正常现象**

2. 再使用requirements.txt文件，安装依赖:

```shell
pip install -r requirements.txt --ignore-installed # 利用requirements.txt文件安装
# 或者
pip install --ignore-installed \
torch==1.10.1 \
numpy==1.21 \
langid \
pydub \
tencentcloud-sdk-python # 使用命令直接安装
```

ps: 其实是我踩过的坑。。`pytorch`的版本必须和`numpy`的版本严格相关，否则无法运行。。

安装完成以后，@bot输入想要bot说的话，bot就可以进行复读啦！

在配置文件`config.yaml`中提供语音模型修改详细见更新

### 使用方法

如需使用tts，请到~/configs/config.yaml中修改 相关配置

* 在 https://console.cloud.tencent.com/tts 启用腾讯云TTS
* 在 https://console.cloud.tencent.com/cam/capi 创建访问密钥，并记录下来
* 修改config.yaml文件的相应配置

使用：

```
@Bot 说 [你想要bot说的话]
```

修改模型的方法：

```
显示模型 # 显示出可供修改的模型
# 修改指令
修改模型 [序号]\[模型名称]
开启/关闭tts 切换使用腾讯TTS(需要配置secret_key)
重载模型 进行模型重载(并没有什么卵用，或许以后内存泄漏解决会有用？)
调整/修改精度 修改语音合成精度(对TTS无效)
调整/修改句长 修改语音合成最大句长(对TTS无效)
```

### 欢迎pr提供模型和模型下载地址

在 [nonebot_plugin_mockingbird/resource/model_list.json](https://github.com/AkashiCoin/nonebot_plugin_mockingbird/blob/master/nonebot_plugin_mockingbird/resource/model_list.json) 中添加

json 模板
```json
{
  "azusa": {
    "nickname": "阿梓语音",
    "url": {
      "record_url": "https://pan.yropo.top/home/source/mockingbird/azusa/record.wav",
      "model_url": "https://pan.yropo.top/home/source/mockingbird/azusa/azusa.pt"
    }
  }
}
```

### 更新

**2022/05/22**

* fix bug [#37](https://github.com/zhenxun-org/nonebot_plugins_zhenxun_bot/issues/37)

**2022/05/21**\[1.0]

* 更换使用MockingBirdForUse库
* 配置文件修改为~/data/mockingbird/config.json
* 支持更新模型列表

**2022/05/18**

* 修复下载路径不可用的问题

**2022/04/18**

* 添加模型 ltyai --- ？
* 添加模型 tianyi --- 洛天依语音-wq

**2022/04/11**\[v0.2]

* 添加腾讯云TTS模式
* 添加模型参数调整功能
* 优化相关代码
* 添加模型nanami1 --- 七海语音
* 添加模型nanmei --- 小南梅语音

**2022/04/09**\[v0.1]

* 真寻beta2适配
* 提供azusa --- 阿梓语音模型
* 修改为异步加载
* 添加热更换模型功能

### 特别感谢

* [MeetWq/MockingBirdForUse](https://github.com/MeetWq/MockingBirdForUse)