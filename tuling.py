import requests, json, time, random, os, hashlib
from playsound import playsound
from config import TULINGS
from speech import baidu_tts
from music import music

class TulingMiddleware(object):
	def handle(self, context):
		print('图灵：', context)
		if (len(context) >= 2):
			self.tuling_ai(context)
		return False

	def tuling_ai(self, context):
		i = random.randint(0, len(TULINGS) - 1)
		data = {
			'reqType': 0,
			'perception': {
				'inputText': { 'text': context }
			},
			'userInfo': {
				'apiKey': TULINGS[i]['API_KEY'],
				'userId': str(random.randint(1, 1000000000000000000000))
			}
		}
		data = json.dumps(data)
		response = requests.post('http://openapi.tuling123.com/openapi/api/v2', data=data)
		data = json.loads(response.text)
		if not 'results' in data: return
		for item in data['results']:
			if (item['resultType'] != 'text'): continue
			text = item['values']['text']
			print('图灵：', text)
			if not os.path.exists('tts-wav/'): os.mkdir('tts-wav/')
			filename = 'tts-wav/%s.mp3'%hashlib.md5(text.encode()).hexdigest()
			baidu_tts(text, filename)
			if music.playing == 1 and text: music.pause_play();
			time.sleep(0.5)
			playsound(filename)
			time.sleep(0.5)
			if music.playing == 2 and text: music.continue_play();

tuling = TulingMiddleware()

if __name__ == "__main__":
	tuling.handle('你好')

