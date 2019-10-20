ai-robot
======
ai-robot是一个中文人工智能机器人。支持语音唤起、智能音箱、对话机器人项目

安装第三方工具
```
#树莓派安装
sudo apt install python-pyaudio python3-pyaudio sox swig libatlas-base-dev mplayer -y
#MAC安装
brew install swig portaudio sox mplayer
```

编译_snowboydetect.so文件
```
git clone https://github.com/Kitt-AI/snowboy
cd snowboy/swig/Python3
make
cp _snowboydetect.so ai-robot/
```

免费申请百度语音识别、图灵机器人
```
1，百度语音识别申请：http://ai.baidu.com/
2，图灵机器人申请：http://www.turingapi.com/
3，申请成功后更改config.py文件中的BAIDUS和TULINGS变量
```

安装启动方法：
```
git clone https://github.com/LiveXY/ai-robot
cd ai-robot/
pip3 install -r requirements.txt
python3 app.js
```

语音测试
```
说：“小白” 可语音唤起，叮一声后录音
说：“播放音乐” 咚一声后开始播放音乐

说：“小白” 唤起后说 “播放下一首”
说：“小白” 唤起后说 “暂停播放”
说：“小白” 唤起后说 “继续播放”
说：“小白” 唤起后说 “循环播放”
说：“小白” 唤起后说 “下载音乐陈雪凝的绿色”
说：“小白” 唤起后说 “播放陈雪凝的绿色”
说：“小白” 唤起后说 “快进”
说：“小白” 唤起后说 “增加音量”
说：“小白” 唤起后说 “减少音量”

说：“小白” 唤起后说 “武汉天气”
```

更换唤醒词
```
1，登陆https://snowboy.kitt.ai/
2，进入https://snowboy.kitt.ai/dashboard
3，点击“ Create Hotword ”按钮，按提示生成自己的唤醒词并下载到项目的resources目录
4，更改config.py文件中的MODELS变量，如果支持多个唤醒词使用逗号分隔（同时要更改SENSITIVITY变量）
```

代码文件详解
```
app.py #启动程序
config.py #配置文件
middleware.py #中间件
music.py #音乐中间件
snowboydecoder.py #snowboy唤起识别
snowboydetect.py #snowboy官方代码
speech.py #语音识别
tuling.py #图灵中间件
```