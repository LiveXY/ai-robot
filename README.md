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

安装启动方法：
```
git clone https://github.com/LiveXY/ai-robot
cd ai-robot/
pip3 install -r requirements.txt
python3 app.js
```

语音测试
```
说：“小白” 可语音唤起，叮一声后
说：“播放音乐”
说：“小白” 唤起后说 “播放下一首”
说：“小白” 唤起后说 “暂停播放”
说：“小白” 唤起后说 “继续播放”
说：“小白” 唤起后说 “武汉天气”
```

文件详解
```
app.py #启动程序
config.py #配置文件
middleware.py #中间件
music.py #音乐中间件
music.py #音乐中间件
snowboydecoder.py #snowboy唤起识别
snowboydetect.py #snowboy官方代码
speech.py #语音识别
tuling.py #图灵
```