import signal
from snowboydecoder import signal_handler, HotwordDetector
from config import RESOURCE_FILE, DETECT_DING, DETECT_DONG, MODELS, SENSITIVITY
from middleware import middleware
from music import music
from tuling import tuling

signal.signal(signal.SIGINT, signal_handler)
middleware.use(music);
middleware.use(tuling);

def processDetected(context):
    print('接收到指令：%s'%context)
    middleware.handle(context)

detector = HotwordDetector(
	model_str = MODELS,
	resource_filename = RESOURCE_FILE,
	sensitivity = SENSITIVITY
)
detector.start(
	detected_callback = processDetected,
	ding_filename = DETECT_DING,
	dong_filename = DETECT_DONG
)

detector.terminate()
