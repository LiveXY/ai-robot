import sys, signal, os, time, collections, wave
import pyaudio
import snowboydetect
from speech import baidu_asr
from music import music

interrupted = False

def signal_handler(signal, frame):
	global interrupted
	interrupted = True

def play_audio_file(fname):
	ding_wav = wave.open(fname, 'rb')
	ding_data = ding_wav.readframes(ding_wav.getnframes())
	audio = pyaudio.PyAudio()
	stream_out = audio.open(
		format = audio.get_format_from_width(ding_wav.getsampwidth()),
		channels = ding_wav.getnchannels(),
		rate = ding_wav.getframerate(),
		input=False, output=True
	)
	stream_out.start_stream()
	stream_out.write(ding_data)
	time.sleep(0.2)
	stream_out.stop_stream()
	stream_out.close()
	audio.terminate()

def save_wave_file(filename, data):
	wf = wave.open(filename, 'wb')
	wf.setnchannels(1)
	wf.setsampwidth(2)
	wf.setframerate(16000)
	wf.writeframes(b"".join(data))
	wf.close()

class HotwordDetector(object):
	def __init__(self, model_str, resource_filename, sensitivity, audio_gain = 1):
		self.detector = snowboydetect.SnowboyDetect(
			resource_filename = resource_filename.encode(),
			model_str = model_str.encode()
		)
		self.detector.SetSensitivity(sensitivity.encode())
		self.detector.SetAudioGain(audio_gain)

		self.ring_buffer = collections.deque(maxlen=(self.detector.NumChannels() * self.detector.SampleRate()*5))

		self.audio = pyaudio.PyAudio()
		self.stream_in = self.audio.open(
			format = self.audio.get_format_from_width(self.detector.BitsPerSample()/8),
			channels = self.detector.NumChannels(),
			rate = self.detector.SampleRate(),
			frames_per_buffer = 2048,
			stream_callback = self.audio_stream_callback,
			input = True, output = False
		)

		print('量化位数：%d'%self.audio.get_format_from_width(self.detector.BitsPerSample()/8))
		print('声道数：%d'%self.detector.NumChannels())
		print('频率：%d'%self.detector.SampleRate())
		print('关键词：%d'%self.detector.NumHotwords())
		print('等待语音激活...')

	def audio_stream_callback(self, in_data, frame_count, time_info, status):
		self.ring_buffer.extend(in_data)
		play_data = chr(0) * len(in_data)
		return play_data, pyaudio.paContinue

	def start(self, detected_callback, ding_filename, dong_filename, sleep_time = 0.03):
		global interrupted

		if interrupted: return
		rec_count = 0; sil_count = 0; save_buffer = []
		while True:
			if interrupted: break

			data = bytes(bytearray(self.ring_buffer))
			self.ring_buffer.clear()

			if len(data) == 0:
				time.sleep(sleep_time)
				continue

			ans = self.detector.RunDetection(data)
			if ans is 1:
				print('语音激活成功！')
				play_audio_file(ding_filename)
				save_buffer = []
				rec_count = 1
				data = bytes(bytearray(self.ring_buffer))
				self.ring_buffer.clear()
			elif ans is 0:
				if rec_count > 0:
					print('正在接收指令：', rec_count)
					save_buffer.append(data)
					rec_count += 1
					sil_count = 0
					if (rec_count > 60):
						ans = -2
						sil_count = 3
			elif ans is -2:
				if rec_count > 0:
					if music.playing == 1: music.pause_play();
					save_buffer.append(data)
					sil_count += 1
					print('等待指令：', sil_count)
					if (sil_count > 30):
						print('接收指令超时！')
						rec_count = 0
						sil_count = 0
						save_buffer = []
				if sil_count > 2 and rec_count > 1:
					play_audio_file(dong_filename)
					if not os.path.exists('temp/'): os.mkdir('temp/')
					if not os.path.exists('cmd-wav/'): os.mkdir('cmd-wav/')
					filename = "temp/rec.wav"
					save_wave_file(filename, save_buffer)
					text = baidu_asr(filename)
					md5file = "cmd-wav/%s.wav"%text
					if not os.path.exists(md5file): os.rename(filename, md5file)
					detected_callback(text)
					rec_count = 0
					sil_count = 0
					save_buffer = []
					print('等待语音激活...')

	def terminate(self):
		self.stream_in.stop_stream()
		self.stream_in.close()
		self.audio.terminate()





