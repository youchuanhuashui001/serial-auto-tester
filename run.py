import sys
import os

def list_cases():
	print("Available cases in 'cases/':")
	for f in os.listdir("cases"):
		if f.endswith(".py") and f != "__init__.py":
			print(f"  - {f[:-3]}")

def run_case(name):
	case_path = f"cases/{name}.py"
	if os.path.exists(case_path):
		print(f"--- Running Test Case: {name} ---")
		# 动态导入并运行脚本中的 run_automation 函数（如果存在）
		os.system(f"python3 {case_path}")
	else:
		print(f"Error: Case '{name}' not found.")
		list_cases()

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: python3 run.py [case_name]")
		list_cases()
	else:
		run_case(sys.argv[1])
