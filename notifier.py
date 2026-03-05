import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header

class EmailNotifier:
	def __init__(self, config):
		self.config = config

	def send(self, subject, content, attachment_path=None, is_html=True):
		"""
		发送邮件，支持附件和 HTML 格式
		:param subject: 主题
		:param content: 正文 (纯文本或 HTML)
		:param attachment_path: 附件文件路径
		:param is_html: 是否为 HTML 格式
		"""
		# 创建一个带附件的实例
		message = MIMEMultipart()
		message['From'] = self.config['sender']
		message['To'] = self.config['receiver']
		message['Subject'] = Header(subject, 'utf-8')

		# 邮件正文
		msg_type = 'html' if is_html else 'plain'
		message.attach(MIMEText(content, msg_type, 'utf-8'))

		# 添加附件
		if attachment_path and os.path.exists(attachment_path):
			try:
				with open(attachment_path, "rb") as f:
					part = MIMEApplication(f.read())
					# 设置附件名
					filename = os.path.basename(attachment_path)
					part.add_header('Content-Disposition', 'attachment', filename=filename)
					message.attach(part)
			except Exception as e:
				print(f"Failed to attach file: {e}")

		try:
			with smtplib.SMTP_SSL(self.config['smtp_server'], self.config['smtp_port']) as server:
				server.login(self.config['sender'], self.config['password'])
				server.sendmail(self.config['sender'], [self.config['receiver']], message.as_string())
			print(f"Email with attachment sent successfully to {self.config['receiver']}")
			return True
		except Exception as e:
			print(f"Failed to send email: {e}")
			return False
