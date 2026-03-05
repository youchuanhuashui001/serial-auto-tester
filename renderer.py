# renderer.py
class ReportRenderer:
	@staticmethod
	def render(metadata, results):
		"""渲染 HTML 报告模板"""
		html = f"""
<html>
<body style="font-family: sans-serif; color: #333; line-height: 1.6;">
	<div style="max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd;">
		<h2>测试概览 (Test Information)</h2>
		<div style="background-color: #f9f9f9; padding: 15px; border-left: 5px solid #333;">
			<p><strong>开始时间:</strong> {metadata.get('start_time')}</p>
			<p><strong>串口端口:</strong> {metadata.get('port')}</p>
			<p><strong>通信参数:</strong> {metadata.get('baudrate')} baud</p>
			<p><strong>日志文件:</strong> {metadata.get('log_file')}</p>
		</div>

		<h2>测试结果 (Test Results)</h2>
		<table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
			<thead>
				<tr style="background-color: #eee; text-align: left;">
					<th style="padding: 10px; border: 1px solid #ddd;">测试项目</th>
					<th style="padding: 10px; border: 1px solid #ddd;">状态</th>
					<th style="padding: 10px; border: 1px solid #ddd;">详细描述</th>
				</tr>
			</thead>
			<tbody>
"""
		
		for res in results:
			html += f"""
				<tr>
					<td style="padding: 10px; border: 1px solid #ddd;">{res['item']}</td>
					<td style="padding: 10px; border: 1px solid #ddd;">{res['status']}</td>
					<td style="padding: 10px; border: 1px solid #ddd;">{res['msg']}</td>
				</tr>
"""
			
		html += """
			</tbody>
		</table>

		<div style="margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px; text-align: right; font-style: italic; color: #777;">
			Sent by: serial-auto-tester v1.0
		</div>
	</div>
</body>
</html>
"""
		return html
