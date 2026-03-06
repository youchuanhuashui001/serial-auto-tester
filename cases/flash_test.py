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
	"check_otptest": True,           # 是否测试 flash otptest
	"check_wptest": True,            # 是否测试 flash wptest (耗时较长)
	"check_multiprogramtest": True,  # 是否测试 flash multiprogramtest
	"check_comtest": True,           # 是否测试 flash comtest (耗时非常久)
}

def test_flash_uid(tester):
	print("\n[STEP] Testing 'flash uid'...")
	tester.send_cmd("flash uid")
	lines = tester.get_response(timeout=3, end_pattern="boot>")
	has_uid = any("uid:" in l for l in lines)
	if has_uid:
		print(f"  \033[32m[PASS] Flash UID 读取成功\033[0m")
		return True
	else:
		print(f"  \033[31m[FAIL] Flash UID 读取失败\033[0m")
		return False

def test_flash_otptest(tester):
	print("\n[STEP] Testing 'flash otptest'...")

	# =========================================================
	# 阶段1: 全量解锁测试 — 所有 region 都应该是 unlock 且读写通过
	# =========================================================
	print("  [阶段1] 发送 'flash otptest' (全量测试)...")
	tester.send_cmd("flash otptest")
	lines = tester.get_response(timeout=15, end_pattern="boot>")

	total_regions = 0
	region_success_count = 0

	for line in lines:
		line = line.strip()
		if not line: continue

		# 检测是否不支持 OTP
		if "not support otp" in line:
			print("  \033[31m[FAIL] 不支持 OTP\033[0m")
			return False

		# 解析 region 数量
		match_count = re.search(r"otp contain (\d+) region", line)
		if match_count:
			total_regions = int(match_count.group(1))
			print(f"  [INFO] 检测到 {total_regions} 个 OTP Region")
			continue

		# 检测到 lock 状态 → 阶段1 不应出现
		match_region = re.search(r"otp region (\d+) (unlock|lock)", line)
		if match_region:
			region_id = int(match_region.group(1))
			state = match_region.group(2)
			if state == "lock":
				print(f"  \033[31m[FAIL] 阶段1: Region {region_id} 不应为 lock 状态\033[0m")
				return False
			continue

		# 统计读写通过的 region
		match_finish = re.search(r"otp region (\d+) test finish", line)
		if match_finish:
			region_success_count += 1

	if total_regions == 0:
		print("  \033[31m[FAIL] 未检测到 OTP Region 数量\033[0m")
		return False

	if region_success_count != total_regions:
		print(f"  \033[31m[FAIL] 阶段1: 仅 {region_success_count}/{total_regions} 个 Region 读写通过\033[0m")
		return False

	print(f"  \033[32m[PASS] 阶段1: 所有 {total_regions} 个 Region 均为 unlock 且读写通过\033[0m")

	# =========================================================
	# 阶段2: 逐个 region 锁定后验证 — 锁定后应为 lock 且读写出错
	# =========================================================
	for i in range(total_regions):
		print(f"  [阶段2] Region {i}/{total_regions - 1}:")

		# 2a. 切换 region
		print(f"    发送 'sflash_otp setregion {i}'...")
		tester.send_cmd(f"sflash_otp setregion {i}")
		lines = tester.get_response(timeout=3, end_pattern="boot>")
		expected_str = f"otp region change => [{i}] success"
		if not any(expected_str in l for l in lines):
			print(f"    \033[31m[FAIL] 切换 Region {i} 失败，未检测到: {expected_str}\033[0m")
			return False
		print(f"    \033[32m[OK] 切换 Region {i} 成功\033[0m")

		# 2b. 锁定当前 region
		print(f"    发送 'flash otplock'...")
		tester.send_cmd("flash otplock")
		tester.get_response(timeout=3, end_pattern="boot>")

		# 2c. 测试锁定后的 region
		print(f"    发送 'flash otptest {i}'...")
		tester.send_cmd(f"flash otptest {i}")
		lines = tester.get_response(timeout=10, end_pattern="boot>")

		found_lock = False
		found_rw_error = False
		for line in lines:
			line = line.strip()
			match_region = re.search(r"otp region (\d+) lock", line)
			if match_region and int(match_region.group(1)) == i:
				found_lock = True
			if "read otp offset readbuf[0] not 0xff" in line:
				found_rw_error = True

		if not found_lock:
			print(f"    \033[31m[FAIL] Region {i} 锁定后未检测到 lock 状态\033[0m")
			return False
		if not found_rw_error:
			print(f"    \033[31m[FAIL] Region {i} 锁定后未检测到预期读写错误\033[0m")
			return False

		print(f"    \033[32m[PASS] Region {i} 锁定验证通过 (lock + 读写出错)\033[0m")

	print(f"  \033[32m[PASS] 阶段2: 所有 {total_regions} 个 Region 锁定验证通过\033[0m")
	return True

def test_flash_wptest(tester):
	print("\n[STEP] Testing 'flash wptest'...")
	print("\033[33m提示: 此项测试耗时较长 (4-5 分钟)，请观察控制台输出。\033[0m")
	tester.send_cmd("flash wptest")
	lines = tester.get_response(timeout=600, end_pattern="boot>")
	if any("boot>" in l for l in lines):
		print("\033[32m[DONE] flash wptest 运行完毕，请查阅日志以判定结果。\033[0m")
		return True
	else:
		return False

def test_flash_multiprogramtest(tester, count=3):
	print(f"\n[STEP] Testing 'flash multiprogramtest' ({count} iterations)...")

	for i in range(1, count + 1):
		print(f"\n>>> Running Iteration {i}/{count}...")
		tester.send_cmd("flash multiprogramtest")

		# 单次超时 5 分钟
		lines = tester.get_response(timeout=300, end_pattern="boot>")

		is_fail = False
		for line in lines:
			if "compare random data fail" in line:
				is_fail = True
				break

		if is_fail:
			print(f"\033[31m[FAIL] Iteration {i} failed\033[0m")
			return False

		if not any("boot>" in l for l in lines):
			print(f"\033[31m[FAIL] Iteration {i} timed out\033[0m")
			return False

		print(f"\033[32m[PASS] Iteration {i} finished successfully.\033[0m")
		# 两次测试之间稍微停顿，让设备喘口气
		time.sleep(1)

	return True

# 失败特征字符串列表
COMTEST_FAIL_PATTERNS = [
	"error: cann't find flash type.",
	"sflash_test_failed:addr=",
	"malloc failed.malloc len=",
	"erase error, i =",
	"cmp error. i =",
]

def test_flash_comtest(tester):
	print("\n[STEP] Testing 'flash comtest'...")
	print("\033[33m提示: 此项测试耗时非常久 (可能数小时)，请耐心等待。\033[0m")
	tester.send_cmd("flash comtest")

	import queue as _queue
	# 超时 12 小时，逐行实时检测
	timeout = 43200
	start_time = time.time()

	while time.time() - start_time < timeout:
		try:
			line = tester.line_queue.get(timeout=0.5)
		except _queue.Empty:
			continue

		line_stripped = line.strip()

		# 实时检测失败特征字符串，发现即刻返回
		for pattern in COMTEST_FAIL_PATTERNS:
			if pattern in line_stripped:
				print(f"  \033[31m[FAIL] 检测到错误: {line_stripped}\033[0m")
				return False

		# 检测通过标志
		if "flash comtest finished." in line_stripped:
			print("  \033[32m[PASS] flash comtest 测试通过\033[0m")
			return True

	print("  \033[31m[FAIL] 未检测到 'flash comtest finished.' 完成标志\033[0m")
	return False

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
			success = test_flash_uid(tester)
			results.append(("Flash UID", success))

		if TEST_ITEMS.get("check_otptest"):
			success = test_flash_otptest(tester)
			results.append(("Flash OTP", success))

		if TEST_ITEMS.get("check_wptest"):
			success = test_flash_wptest(tester)
			results.append(("Flash WP", success))

		if TEST_ITEMS.get("check_multiprogramtest"):
			success = test_flash_multiprogramtest(tester, count=3)
			results.append(("Flash MultiProg", success))

		if TEST_ITEMS.get("check_comtest"):
			success = test_flash_comtest(tester)
			results.append(("Flash ComTest", success))

		# 3. 汇总报告并准备结构化数据
		print("\n" + "="*40)
		print("       FINAL TEST REPORT")
		print("="*40)

		all_pass = True
		formatted_results = []

		for name, success in results:
			status = "PASS" if success else "FAIL"
			status_color = "\033[32mPASS\033[0m" if success else "\033[31mFAIL\033[0m"

			print(f"{name:18} : {status_color}")

			if not success: all_pass = False

			# 添加到结构化结果列表
			formatted_results.append({
				"item": name,
				"status": status
			})

		print("="*40)

		# 4. 发送通知 (传递结构化列表)
		subject = "serial-auto-tester: flash test"
		tester.notify_user(subject, formatted_results, attachment_path=tester.log_file)

	except Exception as e:
		print(f"Runtime error: {e}")
	finally:
		tester.stop()

if __name__ == "__main__":
	run_test()
