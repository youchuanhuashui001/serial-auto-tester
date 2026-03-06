# renderer.py
class ReportRenderer:
	@staticmethod
	def render(metadata, results):
		"""渲染结构化的纯文本报告"""
		# 1. 测试概览
		report = "=== 测试概览 (Test Information) ===\n"
		report += f"开始时间: {metadata.get('start_time')}\n"
		report += f"串口端口: {metadata.get('port')}\n"
		report += f"通信参数: {metadata.get('baudrate')} baud\n"
		report += f"日志文件: {metadata.get('log_file')}\n\n"

		# 2. 测试结果 (模拟表格对齐)
		report += "=== 测试结果 (Test Results) ===\n"
		# 表头
		report += f"{'测试项目':<20} | {'状态':<8}\n"
		report += "-" * 40 + "\n"

		for res in results:
			item = res['item']
			status = res['status']
			report += f"{item:<20} | {status:<8}\n"

		# 3. 工具信息
		report += "\n" + "-" * 60 + "\n"
		report += "Sent by: serial-auto-tester\n"

		return report
