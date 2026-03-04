import serial
import threading
import time
from datetime import datetime
import os
import queue
from config import COLOR_RESET, COLOR_TX, MAIL_CONFIG, LOG_DIR, ENABLE_EMAIL
from notifier import EmailNotifier

class SerialTester:
	def __init__(self, port, baudrate=115200, log_file=None):
		self.port = port
		self.baudrate = baudrate
		if not log_file:
			log_file = os.path.join(LOG_DIR, f"serial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
		self.log_file = log_file
		self.ser = None
		self.is_running = False
		self.reader_thread = None
		self.keywords = {}
		self.notifier = EmailNotifier(MAIL_CONFIG)
		self.line_queue = queue.Queue()

	def start(self):
		try:
			self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
			self.is_running = True
			self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
			self.reader_thread.start()
			print(f"Serial port {self.port} started. Logging to {self.log_file}")
		except serial.SerialException as e:
			print(f"Error opening serial port {self.port}: {e}")
			raise

	def set_keywords(self, kw_dict):
		self.keywords = kw_dict

	def _apply_colors(self, text):
		for word, color_code in self.keywords.items():
			if word in text:
				text = text.replace(word, f"{color_code}{word}{COLOR_RESET}")
		return text

	def _read_loop(self):
		log_dir = os.path.dirname(os.path.abspath(self.log_file))
		if log_dir and not os.path.exists(log_dir):
			os.makedirs(log_dir)

		with open(self.log_file, "a") as f:
			while self.is_running:
				if self.ser and self.ser.in_waiting:
					try:
						line = self.ser.readline().decode('utf-8', errors='ignore')
						if line:
							timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
							f.write(f"[{timestamp}] [RX] << {line}")
							f.flush()
							self.line_queue.put(line)
							colored_line = self._apply_colors(line.strip())
							if colored_line:
								print(f"[{timestamp}] [RX] << {colored_line}")
					except Exception as e:
						print(f"Read error: {e}")
				time.sleep(0.001)

	def send_cmd(self, cmd):
		if not self.ser: return
		if not cmd.endswith("\n"): cmd += "\n"
		timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
		print(f"{COLOR_TX}[{timestamp}] [TX] >> {cmd.strip()}{COLOR_RESET}")
		with open(self.log_file, "a") as f:
			f.write(f"[{timestamp}] [TX] >> {cmd}")
			f.flush()
		self.ser.write(cmd.encode())

	def wait_for(self, pattern, timeout=10):
		"""简单等待特定字符串"""
		start_time = time.time()
		while time.time() - start_time < timeout:
			try:
				line = self.line_queue.get(timeout=0.1)
				if pattern in line:
					return True
			except queue.Empty:
				continue
		return False

	def get_response(self, timeout=2, end_pattern="boot>"):
		"""
		自动化核心：收集命令执行后直到提示符出现的所有返回行
		"""
		response = []
		start_time = time.time()
		while time.time() - start_time < timeout:
			try:
				line = self.line_queue.get(timeout=0.1)
				response.append(line.strip())
				if end_pattern in line:
					break
			except queue.Empty:
				continue
		return response

	def notify_user(self, subject, content):
		if not ENABLE_EMAIL:
			print(f"\033[33m[SKIP EMAIL]\033[0m {subject}: {content}")
			return True
		return self.notifier.send(subject, content)

	def stop(self):
		self.is_running = False
		if self.reader_thread: self.reader_thread.join(timeout=1)
		if self.ser: self.ser.close()
		print("Serial port closed.")
