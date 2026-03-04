import smtplib
from email.mime.text import MIMEText
from email.header import Header

class EmailNotifier:
	def __init__(self, config):
		self.config = config

	def send(self, subject, content):
		"""发送邮件
		注意：授权码 (auth_code) 需要在 config.py 中填写
		"""
		message = MIMEText(content, 'plain', 'utf-8')
		message['From'] = self.config['sender']
		message['To'] = self.config['receiver']
		message['Subject'] = Header(subject, 'utf-8')

		try:
			# 使用 SSL 连接
			with smtplib.SMTP_SSL(self.config['smtp_server'], self.config['smtp_port']) as server:
				server.login(self.config['sender'], self.config['password'])
				server.sendmail(self.config['sender'], [self.config['receiver']], message.as_string())
			print(f"Email sent successfully to {self.config['receiver']}")
			return True
		except Exception as e:
			print(f"Failed to send email: {e}")
			return False
