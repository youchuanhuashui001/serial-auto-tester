import sys
import os
import time

# 导入核心模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import SerialTester
from config import SERIAL_CONFIG, DEFAULT_KEYWORDS

def test_flash():
	tester = SerialTester(SERIAL_CONFIG['port'], SERIAL_CONFIG['baudrate'])
	tester.set_keywords(DEFAULT_KEYWORDS)
	
	try:
		tester.start()
		print(">>> 正在等待开发板就绪 (boot>)...")
		
		# 1. 自动进入命令行
		if not tester.wait_for("Hit any key", timeout=20):
			print("未检测到启动提示")
		tester.send_cmd(" ")
		
		if not tester.wait_for("boot>", timeout=5):
			print("[FAIL] 无法进入 bootloader 命令行")
			return

		# ---------------------------------------------------------
		# 2. 测试 flash uid
		# ---------------------------------------------------------
		tester.send_cmd("flash uid")
		lines = tester.get_response(timeout=3, end_pattern="boot>")
		has_uid = any("uid:" in l for l in lines)
		if has_uid:
			print("[PASS] flash uid 命令正常")
		else:
			print("[FAIL] flash uid 未返回有效结果")

		# ---------------------------------------------------------
		# 3. 测试 flash otptest
		# ---------------------------------------------------------
		print("\n--- 开始 OTP 测试 ---")
		tester.send_cmd("flash otptest")
		# OTP 测试可能较慢，给 10 秒超时
		lines = tester.get_response(timeout=10, end_pattern="boot>")
		
		is_fail = False
		fail_reason = ""
		current_region = ""
		current_state = "" # unlock or lock

		for line in lines:
			# 检测不支持的情况
			if "not support otp" in line:
				is_fail = True
				fail_reason = "不支持 OTP (not support otp)"
				break
			
			# 检测 Region 状态
			if "otp region" in line and ("unlock" in line or "lock" in line):
				current_region = line.strip()
				current_state = "unlock" if "unlock" in line else "lock"
				print(f"检测到阶段: {current_region}")

			# 在 Unlock 状态下检测失败
			if current_state == "unlock":
				if "fail" in line.lower() or "not 0xff" in line:
					is_fail = True
					fail_reason = f"{current_region} 处于 unlock 状态，但操作失败: {line}"
					break
			
			# 在 Lock 状态下，失败是正常的，我们不做 is_fail=True 处理
			if current_state == "lock":
				if "not 0xff" in line or "fail" in line.lower():
					print(f"[INFO] {current_region} 处于 lock 状态，操作失败符合预期。")

		# ---------------------------------------------------------
		# 4. 汇总结果
		# ---------------------------------------------------------
		if is_fail:
			result_msg = f"Flash 测试失败: {fail_reason}"
			print(f"\033[31m{result_msg}\033[0m")
			tester.notify_user("Flash Test: FAIL", result_msg)
		else:
			result_msg = "Flash OTP & UID 测试全部通过！"
			print(f"\033[32m{result_msg}\033[0m")
			tester.notify_user("Flash Test: PASS", result_msg)

	except Exception as e:
		print(f"运行出错: {e}")
	finally:
		tester.stop()

if __name__ == "__main__":
	test_flash()
