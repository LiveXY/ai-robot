
class Middleware(object):
	def __init__(self):
		self.middlewares = []

	def use(self, func):
		self.middlewares.append(func)

	def handle(self, context):
		for func in self.middlewares:
			if not func.handle(context): break

middleware = Middleware()

if __name__ == "__main__":
	from music import music
	from tuling import tuling
	middleware.use(music)
	middleware.use(tuling)
	middleware.handle('你好')

