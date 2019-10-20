import re, os, subprocess, random, threading, time, hashlib
from playsound import playsound
import requests
from config import MUSIC_PATH
from speech import baidu_tts

class MusicMiddleware(object):
	def __init__(self):
		self.music_list = []
		self.player_handler = None
		self.playing = 0;
		self.current_list = []
		self.current_index = 0
		self.shuffle = False
		self.loop = False
		self.exit = False
		self.load_music()

	def handle(self, context):
		text = re.compile(r",|\?|\.|、|，|？|。").sub("", context)
		print('音乐：', text)
		if text in ['播放下一曲', '播放下一个', '播放下个', '播放下一首']: return self.quit_play()
		if text in ['播放上一曲', '播放上一个', '播放上个', '播放上一首']:
			self.current_index = self.current_index - 2
			return self.quit_play()
		if text in ['关闭音乐', '关掉音乐', '关音乐']: return self.close_music()

		if music.playing == 2:
			music.continue_play();
			time.sleep(0.5)
			if text in ['快进', '向前进']: return self.forward()
			if text in ['后退', '向后退']: return self.backward()
			if text in ['加大音量', '增加音量']: return self.inc_volume()
			if text in ['减小音量', '减少音量', '降低音量']: return self.dec_volume()
			if text in ['暂停音乐', '暂停播放', '音乐暂停'] and self.playing == 1: return self.pause_play()

		if music.playing == 0:
			if text in ['随机播放音乐', '随机播放', '随机听歌']: return self.play_music(shuffle=True)
			if text in ['继续播放', '继续播放音乐']: return self.continue_play()
			if text in ['播放音乐', '打开音乐', '音乐走起', '好想听歌', '我要听音乐', '我要听歌', '音乐嗨起来', '嗨起来']: return self.play_music()

			search = self.re_searchs(text, [r'我要听(.*?)的(.*)', r'播放(.*?)的(.*)'])
			if search: return self.play_music(name=search[1], singer=search[0])

			search = self.re_searchs(text, [r'我要听(.*)', r'播放(.*)', r'打开(.*?)音乐', r'打开音乐(.*)'])
			if search: return self.play_music(name=search)

			search = self.re_searchs(text, [r'循环播放(.*)'])
			if search: return self.play_music(name=search, loop=True)

		search = self.re_searchs(text, [r'搜索(.*?)歌曲', r'搜索(.*?)音乐', r'查找(.*?)音乐', r'搜索歌曲(.*)', r'搜索音乐(.*)'])
		if search: return self.search_music(search)

		search = self.re_searchs(text, [r'下载(.*?)歌曲', r'下载(.*?)音乐'])
		if search: return self.down_music(search)

		return True

	def re_searchs(self, text, list):
		for key in list:
			results = re.findall(key, text, re.M|re.I)
			if results and results[0] and len(results) > 1 and results[1]:
				return [results[0], results[1]]
			if results and results[0]: return results[0]
		return False

	def pause_play(self):
		if self.playing:
			self.playing = 2
			self.player_handler.stdin.write(b'p')
			self.player_handler.stdin.flush()
		return False

	def continue_play(self):
		if self.playing:
			self.playing = 1
			self.player_handler.stdin.write(b'c')
			self.player_handler.stdin.flush()
		return False

	def inc_volume(self):
		if self.playing:
			self.player_handler.stdin.write(b'*')
			self.player_handler.stdin.flush()
		return False

	def dec_volume(self):
		if self.playing:
			self.player_handler.stdin.write(b'/')
			self.player_handler.stdin.flush()
		return False

	def backward(self):
		if self.playing:
			self.player_handler.stdin.write(b'<-')
			self.player_handler.stdin.flush()
		return False

	def forward(self):
		if self.playing:
			self.player_handler.stdin.write(b'->')
			self.player_handler.stdin.flush()
		return False

	def play_music(self, name = None, singer = None, shuffle = False, loop = False):
		if self.playing: return False
		self.exit = False
		print(name, singer, shuffle, loop)
		self.shuffle = shuffle
		self.loop = loop
		list = {}; count = 0;
		#播放全部
		if not name and not singer:
			for item in self.music_list:
				list[item['name']] = item['file']

		if name and singer:
			new = "%s-%s"%(singer, name)
			for item in self.music_list:
				if re.search(new, item['name'], re.M|re.I):
					list[item['name']] = item['file']
					print('查找到：', item)

		if name:
			name = re.compile(r"的音乐|音乐").sub("", name)
			print('查找name：', name)
			for item in self.music_list:
				if re.search(name, item['name'], re.M|re.I):
					list[item['name']] = item['file']
					print('查找到：', item)
		if singer:
			singer = re.compile(r"的音乐|音乐").sub("", singer)
			print('查找singer：', singer)
			for item in self.music_list:
				if re.search(singer, item['name'], re.M|re.I):
					list[item['name']] = item['file']
					print('查找到：', item)

		if len(list) > 0:
			self.current_list.clear()
			for item in list:
				file = list[item]
				self.current_list.append(file)

			if shuffle: random.shuffle(self.current_list)
			self.current_index = 0
			self.play_next()
		else:
			text = ''
			if singer: text = text + singer
			if name: text = text + name
			self.down_music(text)

		return False

	def play_next(self):
		thread = threading.Thread(target=self.mplayer, name="mplayer")
		thread.setDaemon(True)
		thread.start()

	def mplayer(self):
		if (self.current_index < 0 or self.exit): return
		if (self.current_index >= len(self.current_list) - 1):
			if self.loop:
				print('循环播放！')
				if self.shuffle: random.shuffle(self.current_list)
				self.current_index = 0
				return self.play_next()
			print('播放结束！')
			self.playing = 0
			self.current_list.clear()
			self.current_index = 0
			return

		file = self.current_list[self.current_index]
		print('播放音乐：', file)
		self.player_handler = subprocess.Popen(["mplayer", file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		self.playing = 1
		while True:
			if self.exit: break
			strout = self.player_handler.stdout.readline().decode('u8')
			print(strout)
			if strout == 'Exiting... (End of file)\n' or strout == 'Exiting... (Quit)\n':
				self.playing = 0
				break
		self.current_index = self.current_index + 1
		self.play_next()

	def quit_play(self):
		if self.playing:
			self.player_handler.stdin.write(b'q')
			self.player_handler.stdin.flush()
		return False

	def close_music(self):
		self.exit = True
		self.playing = 0
		self.current_list.clear()
		self.current_index = 0
		self.player_handler.stdin.write(b'q')
		self.player_handler.stdin.flush()
		time.sleep(0.5)
		self.player_handler.kill()
		time.sleep(0.5)
		subprocess.run("killall mplayer", shell=True)
		return False

	def add_music(self, name, extension, fullfile):
		self.music_list.append({ 'name': name, 'ext': extension, 'file': fullfile })

	def load_music_file(self, path):
		for i in os.listdir(path):
			filepath = os.path.join(path, i)
			if os.path.isdir(filepath):
				self.load_music_file(filepath)
			else:
				fullfile = os.path.join(path, i)
				filepath, filename = os.path.split(fullfile)
				name, extension = os.path.splitext(filename)
				if extension in ['.mp3', '.flac', '.wav', '.m4a']:
					self.add_music(name, extension, fullfile)

	def load_music(self):
		if (not os.path.exists(MUSIC_PATH)): os.mkdir(MUSIC_PATH)
		self.load_music_file(MUSIC_PATH)
		print('共加载', len(self.music_list), '首音乐！')
		if len(self.music_list) == 0: self.play_text('您还没有音乐，可以通过搜索和下载指令获得您需要的音乐，如：搜索绿色音乐 和 下载绿色音乐');
		else: self.play_text('您有 %s 首音乐，可以通过播放音乐指令播放'%len(self.music_list));

	def search_request(self, keyword):
		params = {"w": keyword, "format": "json", "p": 1, "n": 2}
		session = requests.Session()
		session.headers.update({"referer": "http://m.y.qq.com", "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"})
		resp = session.get("http://c.y.qq.com/soso/fcgi-bin/search_for_qq_cp", params=params, timeout=7)
		if resp.status_code != requests.codes.ok or not resp.text: return False
		list = resp.json().get("data", {}).get("song", {}).get("list", [])
		results = []
		for item in list:
			singers = [s.get("name", "") for s in item.get("singer", "")]
			title = item.get("songname", "")
			singer = "、".join(singers)
			mid = item.get("songmid", "")
			size = round(item.get("size128", 0) / 1048576, 2)
			if size > 0: results.append({'mid': mid, 'singer': singer, 'title': title, 'size': size})
		return results


	def play_text(self, text):
		if not os.path.exists('tts-wav/'): os.mkdir('tts-wav/')
		filename = 'tts-wav/%s.mp3'%hashlib.md5(text.encode()).hexdigest()
		if not os.path.exists(filename): baidu_tts(text, filename)
		if self.playing == 1 and text: self.pause_play();
		time.sleep(0.5)
		playsound(filename)
		time.sleep(0.5)
		if self.playing == 2 and text: self.continue_play();
		return False

	def search_music(self, keyword):
		list = self.search_request(keyword)
		if len(list) > 0:
			text = '搜索到%s个结果：'%len(list)
			for item in list:
				text = text + item['singer'] + '，的，' + item['title'] + '、、'
		else:
			text = '没有搜索到：%s'%keyword
		self.play_text(text)
		return False

	def down_qq_music(self, mid, filename, size):
		guid = str(random.randrange(1000000000, 10000000000))
		params = { "guid": guid, "loginUin": "3051522991", "format": "json", "platform": "yqq", "cid": "205361747", "uin": "3051522991", "songmid": mid, "needNewCode": 0}
		rate_list = [("A000", "ape", 800), ("F000", "flac", 800), ("M800", "mp3", 320), ("C400", "m4a", 128), ("M500", "mp3", 128)]
		session = requests.Session()
		session.headers.update({"referer": "http://y.qq.com"})
		url = ''; ext = '';
		for rate in rate_list:
			params["filename"] = "%s%s.%s" % (rate[0], mid, rate[1])
			resp = session.get("https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg", params=params, timeout=7)
			vkey = resp.json().get("data", {}).get("items", [])[0].get("vkey", "")
			if vkey:
				url = ("http://dl.stream.qqmusic.qq.com/%s?vkey=%s&guid=%s&uin=3051522991&fromtag=64"%(params["filename"], vkey, guid))
				ext = rate[1]
				break

		if len(url) == 0 or len(ext) == 0: return False

		session.headers.update({"referer": "http://m.y.qq.com", "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"})
		res = session.get(url)
		file = '{}/{}.{}'.format(MUSIC_PATH, filename, ext)
		with open(file, 'wb') as f:
			f.write(res.content)
		fsize = os.path.getsize(file)
		if fsize < 10 * 1024:
			os.remove(file)
			return False
		return True

	def down_music(self, keyword):
		list = self.search_request(keyword)
		if len(list) == 0: return self.play_text('没有找到您要的音乐！')
		flag = False
		for item in list:
			filename = '%s-%s'%(item['singer'], item['title'])
			text = '%s，的，%s'%(item['singer'], item['title'])
			result = self.down_qq_music(item['mid'], filename, item['size'])
			if result:
				flag = True
				self.play_text('%s 下载完成！'%text)

		if flag:
			self.music_list.clear();
			self.load_music()

		return False

music = MusicMiddleware()

if __name__ == "__main__":
	search = music.re_searchs('播放陈雪凝的绿色', [r'播放(.*?)的(.*)'])
	print(search[1], search[0])
	#music.search_music("风筝误");
	#music.down_music("风筝误");
	#music.handle("播放风筝误");
	#music.handle("我要听风筝误");
	#music.handle("我要听大壮的我们不一样");
	#music.handle("播放大壮的音乐");
	#music.handle("播放刘德华的音乐");
	#music.handle("你好");
