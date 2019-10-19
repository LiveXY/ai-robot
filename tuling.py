import requests, json, time, random, os
from config import TULINGS
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
			music.play_text(text)

tuling = TulingMiddleware()

if __name__ == "__main__":
	tuling.handle('你好')

