import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import SerialTester
from config import SERIAL_CONFIG, DEFAULT_KEYWORDS, LOG_DIR
import time

def run_automation():
	# 1. 初始化
	tester = SerialTester(
		port=SERIAL_CONFIG['port'], 
		baudrate=SERIAL_CONFIG['baudrate'],
		log_file="auto_test_report.log"
	)
	tester.set_keywords(DEFAULT_KEYWORDS)
	
	try:
		tester.start()
		print(">>> 请给开发板上电或复位...")

		# 2. 等待开发板启动到特定提示符 (超时 30 秒)
		if tester.wait_for("Hit any key to stop autoboot", timeout=30):
			print("[PASS] 检测到启动提示，准备发送按键中断...")
			tester.send_cmd(" ") # 发送空格中断
			
			# 3. 等待进入 boot 提示符
			if tester.wait_for("boot>", timeout=5):
				print("[PASS] 已进入 Bootloader 命令行模式")
				
				# 4. 执行测试命令
				tester.send_cmd("help")
				
				# 检查 help 命令是否输出了某些关键字
				if tester.wait_for("Partition Version", timeout=5):
					msg = "自动化测试成功：成功进入 Bootloader 并执行 help 命令。"
					tester.notify_user("测试结果：PASS", msg)
				else:
					tester.notify_user("测试结果：FAIL", "错误：help 命令未返回预期内容。")
			else:
				tester.notify_user("测试结果：FAIL", "错误：无法进入 boot> 命令行。")
		else:
			tester.notify_user("测试结果：FAIL", "错误：未检测到启动信息，测试超时。")

	except Exception as e:
		print(f"发生异常: {e}")
		tester.notify_user("测试结果：ERROR", f"自动化脚本运行异常: {e}")
	finally:
		tester.stop()
		print("测试完成。")

if __name__ == "__main__":
	run_automation()
