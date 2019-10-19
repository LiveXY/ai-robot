import re, os, subprocess, random, threading, time
from playsound import playsound
from config import MUSIC_PATH

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
		self.load_music_file(MUSIC_PATH)

	def handle(self, context):
		text = re.compile(r",|\?|\.|、|，|？|。").sub("", context)
		print('音乐：', text)
		if text in ['播放下一曲', '播放下一个', '播放下个', '播放下一首']: return self.quit_play()
		if text in ['播放上一曲', '播放上一个', '播放上个', '播放上一首']:
			self.current_index = self.current_index - 1
			return self.quit_play()
		if text in ['关闭音乐', '关掉音乐', '关音乐', '暂停音乐', '音乐暂停']: return self.close_music()

		if music.playing == 2:
			music.continue_play();
			time.sleep(0.5)
			if text in ['快进', '向前进']: return self.forward()
			if text in ['后退', '向后退']: return self.backward()
			if text in ['加大音量', '增加音量']: return self.inc_volume()
			if text in ['减小音量', '减少音量', '降低音量']: return self.dec_volume()
			if text in ['暂停音乐', '暂停播放'] and self.playing == 1: return self.pause_play()

		if music.playing == 0:
			if text in ['随机播放音乐', '随机播放', '随机听歌']: return self.play_music(shuffle=True)
			if text in ['继续播放', '继续播放音乐']: return self.continue_play()
			if text in ['播放音乐', '打开音乐', '音乐走起', '好想听歌', '我要听音乐', '我要听歌', '音乐嗨起来', '嗨起来']: return self.play_music()

			search = re.search(r'我要听(.*?)的(.*)', text, re.M|re.I)
			if search: return self.play_music(name=search.group(2), singer=search.group(1))
			search = re.search(r'播放(.*?)的(.*)', text, re.M|re.I)
			if search: return self.play_music(name=search.group(2), singer=search.group(1))

			search = re.search(r'我要听(.*)', text, re.M|re.I)
			if search: return self.play_music(name=search.group(1))
			search = re.search(r'播放(.*)', text, re.M|re.I)
			if search: return self.play_music(name=search.group(1))
			search = re.search(r'打开(.*?)音乐', text, re.M|re.I)
			if search: return self.play_music(name=search.group(1))

			search = re.search(r'循环播放(.*?)音乐', text, re.M|re.I)
			if search: return self.play_music(name=search.group(1), loop=True)

		search = re.search(r'搜索(.*?)音乐', text, re.M|re.I)
		if search: return self.search_music(search.group(1))
		search = re.search(r'查找(.*?)音乐', text, re.M|re.I)
		if search: return self.search_music(search.group(1))

		search = re.search(r'下载(.*?)音乐', text, re.M|re.I)
		if search: return self.down_music(search.group(1))

		return True

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
			self.play_next(0)

		return False

	def play_next(self, index):
		self.current_index = index
		thread = threading.Thread(target=self.mplayer, args=(index,), name="mplayer")
		thread.setDaemon(True)
		thread.start()

	def mplayer(self, index):
		if (index < 0 or self.exit): return
		if (index >= len(self.current_list)):
			if self.loop:
				print('循环播放！')
				if shuffle: random.shuffle(self.current_list)
				return self.play_next(0)
			print('播放结束！')
			self.playing = 0
		file = self.current_list[index]
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
		self.play_next(index+1)

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
				if extension in ['.mp3', '.flac', '.wav']:
					self.add_music(name, extension, fullfile)

	def load_music(self):
		if (not os.path.exists(MUSIC_PATH)):
			print('音乐路径不存在：', MUSIC_PATH)
			return
		print('共加载', len(self.music_list), '首音乐！')

music = MusicMiddleware()

if __name__ == "__main__":
	music.handle("播放风筝误");
	#music("我要听风筝误");
	#music("我要听大壮的我们不一样");
	#music("播放大壮的音乐");
	#music("播放刘德华的音乐");
	#music("你好");
