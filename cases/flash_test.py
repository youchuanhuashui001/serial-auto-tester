import sys
import os
import time
import re

# 导入核心模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import SerialTester
from config import SERIAL_CONFIG, DEFAULT_KEYWORDS

# ---------------------------------------------------------
# 测试项开关配置
# ---------------------------------------------------------
TEST_ITEMS = {
	"check_uid": True,
	"check_otptest": True,
}

def test_flash_uid(tester):
	"""测试 flash uid"""
	print("\n[STEP] Testing 'flash uid'...")
	tester.send_cmd("flash uid")
	lines = tester.get_response(timeout=3, end_pattern="boot>")
	has_uid = any("uid:" in l for l in lines)
	if has_uid:
		print("\033[32m[PASS] flash uid command works.\033[0m")
		return True, "UID check passed"
	else:
		return False, "UID not found in response"

def test_flash_otptest(tester):
	"""测试 flash otptest (增强版状态机)"""
	print("\n[STEP] Testing 'flash otptest'...")
	tester.send_cmd("flash otptest")
	# OTP 测试包含擦写，超时时间给长一点
	lines = tester.get_response(timeout=15, end_pattern="boot>")
	
	total_regions = 0
	current_region_id = -1
	current_state = "" # unlock or lock
	
	# 状态标志
	found_expected_lock_error = False
	region_success_count = 0

	for line in lines:
		line = line.strip()
		if not line: continue

		# 1. 获取总 Region 数量
		match_count = re.search(r"otp contain (\d+) region", line)
		if match_count:
			total_regions = int(match_count.group(1))
			print(f"检测到总计 {total_regions} 个 OTP Region")
			continue

		# 2. 检测不支持
		if "not support otp" in line:
			return False, "错误: 设备不支持 OTP (not support otp)"

		# 3. 检测当前 Region 及其状态 (unlock/lock)
		match_region = re.search(r"otp region (\d+) (unlock|lock)", line)
		if match_region:
			current_region_id = int(match_region.group(1))
			current_state = match_region.group(2)
			print(f"正在检查 Region {current_region_id} (状态: {current_state})")
			continue

		# 4. 根据状态进行分支判断
		if current_state == "unlock":
			# 必须看到 test finish
			if f"otp region {current_region_id} test finish" in line:
				print(f"\033[32m[OK] Region {current_region_id} (unlock) 测试通过\033[0m")
				region_success_count += 1
				# 继续检查下一个 Region

		elif current_state == "lock":
			# 必须看到特定的报错字符串
			if "read otp offset readbuf[0] not 0xff" in line:
				print(f"\033[32m[PASS] Region {current_region_id} (lock) 报错符合预期，停止后续检查。\033[0m")
				found_expected_lock_error = True
				# 按照规则：一旦 lock 检查成功，不再继续检查
				break

	# 5. 最终判定
	if found_expected_lock_error:
		return True, f"OTP 测试通过 (在 Region {current_region_id} 命中 Lock 预期)"
	
	if total_regions > 0 and region_success_count == total_regions:
		return True, f"OTP 测试通过 (所有 {total_regions} 个 Region 均为 unlock 并通过)"

	# 如果运行结束都没有命中上述逻辑
	return False, f"OTP 测试未完成或结果不符合预期 (Region {current_region_id}, State: {current_state})"

def run_test():
	tester = SerialTester(SERIAL_CONFIG['port'], SERIAL_CONFIG['baudrate'])
	tester.set_keywords(DEFAULT_KEYWORDS)
	
	results = []
	try:
		try:
			tester.start()
		except ConnectionError as e:
			print(e)
			return

		print(">>> 正在尝试进入 bootloader 状态...")
		for i in range(3):
			tester.send_cmd(" ")
			if tester.wait_for("boot>", timeout=2):
				break
			time.sleep(0.5)

		if not tester.wait_for("boot>", timeout=5):
			print("\033[31m[ERROR] Cannot enter bootloader prompt.\033[0m")
			return

		if TEST_ITEMS.get("check_uid"):
			success, msg = test_flash_uid(tester)
			results.append(("Flash UID", success, msg))

		if TEST_ITEMS.get("check_otptest"):
			success, msg = test_flash_otptest(tester)
			results.append(("Flash OTP", success, msg))

		print("\n" + "="*40)
		print("       FINAL TEST REPORT")
		print("="*40)
		all_pass = True
		report_content = ""
		for name, success, msg in results:
			status = "\033[32mPASS\033[0m" if success else "\033[31mFAIL\033[0m"
			print(f"{name:15} : {status} ({msg})")
			report_content += f"{name}: {'PASS' if success else 'FAIL'} ({msg})\n"
			if not success: all_pass = False
		print("="*40)

		subject = "Flash Test: PASS" if all_pass else "Flash Test: FAIL"
		tester.notify_user(subject, report_content)

	except Exception as e:
		print(f"Runtime error: {e}")
	finally:
		tester.stop()

if __name__ == "__main__":
	run_test()
