import time
import signal
import pexpect



class ChildTerminator:
	def __init__(self, child):
		self.child = child

	def _drain_output(self, duration=5):
		end = time.time() + duration
		while time.time() < end:
			if not self.child.isalive():
				return True
			try:
				self.child.read_nonblocking(1024, timeout=0.1)
			except pexpect.exceptions.TIMEOUT:
				pass
			time.sleep(0.1)
		return False

	def terminate(self):
		try:
			self.child.kill(signal.SIGINT)
			if self._drain_output():
				return
			self.child.kill(signal.SIGTERM)
			time.sleep(1)
			if self.child.isalive():
				self.child.kill(signal.SIGKILL)
		except Exception:
			pass