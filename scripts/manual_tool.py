import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import SerialTester
from config import SERIAL_CONFIG, DEFAULT_KEYWORDS, LOG_DIR
import time

def main():
	# 1. 初始化
	tester = SerialTester(
		port=SERIAL_CONFIG['port'], 
		baudrate=SERIAL_CONFIG['baudrate'],
		log_file=os.path.join(LOG_DIR, "manual_test.log")
	)
	
	# 2. 设置高亮关键字 (PASS/FAIL 等)
	tester.set_keywords(DEFAULT_KEYWORDS)
	
	try:
		# 3. 启动
		print("--- Starting Serial Monitoring ---")
		tester.start()
		
		# 4. 模拟发送一些命令给开发板
		time.sleep(1)
		tester.send_cmd("uname -a")
		time.sleep(2)
		tester.send_cmd("ls /")
		
		# 保持监听一段时间，观察开发板的实时打印
		print("\nMonitoring for 10 seconds... (Check for Green/Red colors)")
		time.sleep(10)
		
	except KeyboardInterrupt:
		print("\nInterrupted by user.")
	finally:
		# 5. 停止
		tester.stop()
		print(f"\nTest finished. Log saved to board_test.log")

if __name__ == "__main__":
	main()
