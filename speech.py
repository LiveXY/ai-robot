import random
from aip import AipSpeech
from config import BAIDUS

bai_obj = {}

#百度AI
def baidu():
	i = random.randint(0, len(BAIDUS) - 1)
	key = 'b%s'%i
	if not key in bai_obj:
		obj = BAIDUS[i]
		bai_obj[key] = AipSpeech(obj['APP_ID'], obj['API_KEY'], obj['SECRET_KEY'])
	return bai_obj[key]

#读取文件
def get_file_content(filePath):
	with open(filePath, 'rb') as fp:
		return fp.read()

#语音转文字
def baidu_asr(file_name, lan = 'zh'):
	res = baidu().asr(get_file_content(file_name), 'wav', 16000, {'lan': lan})
	if 'result' in res.keys():
		return res['result'][0]
	else:
		return ''

#文字转语音
def baidu_tts(text, file_name, per = 0):
	result  = baidu().synthesis(text, 'zh', 1, {'vol': 5, 'per': per, 'spd': 7})
	if not isinstance(result, dict):
		with open(file_name, 'wb') as f:
			f.write(result)

if __name__ == "__main__":
	print(baidu_asr('../asr/asr-wav/1.wav'))

