import serial
import threading
import time
from datetime import datetime
import os
import queue
import signal
import fcntl
from config import COLOR_RESET, COLOR_TX, MAIL_CONFIG, LOG_DIR, ENABLE_EMAIL
from notifier import EmailNotifier
from renderer import ReportRenderer

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
		# 记录测试开始时间用于报告展示
		self.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	def _find_occupants(self):
		"""遍历 /proc 查找占用串口的进程"""
		occupants = []
		try:
			for pid_str in os.listdir('/proc'):
				if not pid_str.isdigit(): continue
				pid = int(pid_str)
				fd_dir = os.path.join('/proc', pid_str, 'fd')
				if not os.access(fd_dir, os.R_OK): continue
				try:
					for fd in os.listdir(fd_dir):
						fd_path = os.path.join(fd_dir, fd)
						try:
							link_path = os.readlink(fd_path)
							if link_path == self.port:
								cmdline_path = os.path.join('/proc', pid_str, 'cmdline')
								with open(cmdline_path, 'rb') as f:
									cmd = f.read().replace(b'\x00', b' ').decode().strip()
								occupants.append({'pid': pid, 'cmd': cmd})
								break
						except (OSError, FileNotFoundError): continue
				except (PermissionError, FileNotFoundError): continue
		except Exception as e:
			print(f"Warning during occupancy check: {e}")
		return occupants

	def start(self):
		"""启动串口，带占用检查"""
		while True:
			occupants = self._find_occupants()
			if not occupants: break
			print(f"\n\033[31m[WARNING] 串口 {self.port} 正在被以下进程使用:\033[0m")
			for occ in occupants:
				print(f"  - PID: {occ['pid']}, Command: {occ['cmd']}")
			choice = input(f"\n是否强制关闭这些进程并继续测试? (y/n): ").strip().lower()
			if choice == 'y':
				for occ in occupants:
					try:
						os.kill(occ['pid'], signal.SIGKILL)
						print(f"已发送 SIGKILL 给 PID {occ['pid']}")
					except Exception as e:
						print(f"无法关闭 PID {occ['pid']}: {e}")
				time.sleep(1)
			else:
				raise ConnectionError("用户取消测试，因为串口被占用。")

		try:
			self.ser = serial.Serial(self.port, self.baudrate, timeout=0.5)
			self.is_running = True
			self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
			self.reader_thread.start()
			print(f"Serial port {self.port} started. Logging to {self.log_file}")
		except Exception as e:
			print(f"Error opening serial port: {e}")
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
						if self.is_running:
							print(f"Read error: {e}")
				time.sleep(0.001)

	def send_cmd(self, cmd):
		if not self.ser: return
		while not self.line_queue.empty():
			try: self.line_queue.get_nowait()
			except: break
		if not cmd.endswith("\n"): cmd += "\n"
		timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
		print(f"{COLOR_TX}[{timestamp}] [TX] >> {cmd.strip()}{COLOR_RESET}")
		with open(self.log_file, "a") as f:
			f.write(f"[{timestamp}] [TX] >> {cmd}")
			f.flush()
		self.ser.write(cmd.encode())

	def wait_for(self, pattern, timeout=10):
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

	def notify_user(self, subject, results_list, attachment_path=None):
		"""
		接收结构化的结果列表并渲染 HTML 发送
		:param subject: 邮件主题
		:param results_list: 格式为 [{'item': '...', 'status': 'PASS/FAIL'}] 的列表
		:param attachment_path: 日志文件附件路径
		"""
		if not ENABLE_EMAIL:
			summary = "\n".join([f"{r['item']}: {r['status']}" for r in results_list])
			print(f"\033[33m[SKIP EMAIL]\033[0m {subject}:\n{summary}")
			return True
		
		# 准备元数据
		metadata = {
			"start_time": self.start_time,
			"port": self.port,
			"baudrate": self.baudrate,
			"log_file": self.log_file
		}
		
		# 渲染纯文本报告
		text_content = ReportRenderer.render(metadata, results_list)
		
		# 发送纯文本邮件
		return self.notifier.send(subject, text_content, attachment_path)

	def stop(self):
		"""优雅关闭"""
		self.is_running = False
		if self.reader_thread:
			self.reader_thread.join(timeout=1)
		if self.ser:
			self.ser.close()
			self.ser = None
		print("Serial port closed.")
