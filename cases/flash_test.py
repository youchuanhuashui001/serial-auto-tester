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
	"check_uid": True,               # 是否测试 flash uid
	"check_otptest": False,           # 是否测试 flash otptest
	"check_wptest": False,            # 是否测试 flash wptest (耗时较长)
	"check_multiprogramtest": False,  # 是否测试 flash multiprogramtest
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
	lines = tester.get_response(timeout=15, end_pattern="boot>")
	
	total_regions = 0
	current_region_id = -1
	current_state = "" # unlock or lock
	found_expected_lock_error = False
	region_success_count = 0

	for line in lines:
		line = line.strip()
		if not line: continue
		match_count = re.search(r"otp contain (\d+) region", line)
		if match_count:
			total_regions = int(match_count.group(1))
			print(f"检测到总计 {total_regions} 个 OTP Region")
			continue
		if "not support otp" in line:
			return False, "错误: 设备不支持 OTP (not support otp)"
		match_region = re.search(r"otp region (\d+) (unlock|lock)", line)
		if match_region:
			current_region_id = int(match_region.group(1))
			current_state = match_region.group(2)
			print(f"正在检查 Region {current_region_id} (状态: {current_state})")
			continue
		if current_state == "unlock":
			if f"otp region {current_region_id} test finish" in line:
				print(f"\033[32m[OK] Region {current_region_id} (unlock) 测试通过\033[0m")
				region_success_count += 1
		elif current_state == "lock":
			if "read otp offset readbuf[0] not 0xff" in line:
				print(f"\033[32m[PASS] Region {current_region_id} (lock) 报错符合预期，停止后续检查。\033[0m")
				found_expected_lock_error = True
				break

	if found_expected_lock_error:
		return True, f"OTP 测试通过 (在 Region {current_region_id} 命中 Lock 预期)"
	if total_regions > 0 and region_success_count == total_regions:
		return True, f"OTP 测试通过 (所有 {total_regions} 个 Region 均为 unlock 并通过)"
	return False, f"OTP 测试结果不符合预期 (Region {current_region_id}, State: {current_state})"

def test_flash_wptest(tester):
	"""测试 flash wptest (由用户自行判断 log)"""
	print("\n[STEP] Testing 'flash wptest'...")
	print("\033[33m提示: 此项测试耗时较长 (4-5 分钟)，请观察控制台输出。\033[0m")
	tester.send_cmd("flash wptest")
	lines = tester.get_response(timeout=600, end_pattern="boot>")
	if any("boot>" in l for l in lines):
		print("\033[32m[DONE] flash wptest 运行完毕，请查阅日志以判定结果。\033[0m")
		return True, "Completed (User check log)"
	else:
		return False, "Timed out waiting for 'boot>' prompt"

def test_flash_multiprogramtest(tester, count=3):
	"""测试 flash multiprogramtest (循环 count 次)"""
	print(f"\n[STEP] Testing 'flash multiprogramtest' ({count} iterations)...")
	
	for i in range(1, count + 1):
		print(f"\n>>> Running Iteration {i}/{count}...")
		tester.send_cmd("flash multiprogramtest")
		
		# 单次超时 5 分钟
		lines = tester.get_response(timeout=300, end_pattern="boot>")
		
		is_fail = False
		error_detail = ""
		for line in lines:
			if "compare random data fail" in line:
				is_fail = True
				error_detail = line.strip()
				break
		
		if is_fail:
			msg = f"Iteration {i} failed: {error_detail}"
			print(f"\033[31m[FAIL] {msg}\033[0m")
			return False, msg
		
		if not any("boot>" in l for l in lines):
			msg = f"Iteration {i} timed out waiting for 'boot>' prompt"
			print(f"\033[31m[FAIL] {msg}\033[0m")
			return False, msg
			
		print(f"\033[32m[PASS] Iteration {i} finished successfully.\033[0m")
		# 两次测试之间稍微停顿，让设备喘口气
		time.sleep(1)
	
	return True, f"All {count} iterations passed"

def run_test():
	tester = SerialTester(SERIAL_CONFIG['port'], SERIAL_CONFIG['baudrate'])
	tester.set_keywords(DEFAULT_KEYWORDS)
	
	results = []
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
			else:
				print("\033[31m[FAIL] 已检测到提示但无法进入 boot> 命令行\033[0m")
				return
		else:
			print("\033[31m[FAIL] 等待 'Hit any key' 超时，测试终止\033[0m")
			return

		# 依次执行各测试项
		if TEST_ITEMS.get("check_uid"):
			success, msg = test_flash_uid(tester)
			results.append(("Flash UID", success, msg))

		if TEST_ITEMS.get("check_otptest"):
			success, msg = test_flash_otptest(tester)
			results.append(("Flash OTP", success, msg))

		if TEST_ITEMS.get("check_wptest"):
			success, msg = test_flash_wptest(tester)
			results.append(("Flash WP", success, msg))

		if TEST_ITEMS.get("check_multiprogramtest"):
			success, msg = test_flash_multiprogramtest(tester, count=3)
			results.append(("Flash MultiProg", success, msg))

		# 3. 汇总报告并准备结构化数据
		print("\n" + "="*40)
		print("       FINAL TEST REPORT")
		print("="*40)
		
		all_pass = True
		formatted_results = []
		
		for name, success, msg in results:
			status = "PASS" if success else "FAIL"
			status_color = "\033[32mPASS\033[0m" if success else "\033[31mFAIL\033[0m"
			
			note = " (Manual check log)" if "WP" in name else ""
			print(f"{name:18} : {status_color} ({msg}){note}")
			
			if not success: all_pass = False
			
			# 添加到结构化结果列表
			formatted_results.append({
				"item": name,
				"status": status,
				"msg": msg
			})
			
		print("="*40)

		# 4. 发送通知 (传递结构化列表)
		subject = "Flash Test Summary"
		tester.notify_user(subject, formatted_results, attachment_path=tester.log_file)

	except Exception as e:
		print(f"Runtime error: {e}")
	finally:
		tester.stop()

if __name__ == "__main__":
	run_test()
