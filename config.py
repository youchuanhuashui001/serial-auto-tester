# config.py
SERIAL_CONFIG = {
	"port": "/dev/ttyUSB0",
	"baudrate": 115200,
	"timeout": 1
}

# 默认日志目录
LOG_DIR = "logs"

# 邮件通知开关
ENABLE_EMAIL = False

MAIL_CONFIG = {
	"smtp_server": "smtp.163.com",
	"smtp_port": 465,
	"sender": "tanxzh12123@163.com",
	"password": "AUnZmjKCT5tdMRyW",
	"receiver": "tanxzh@nationalchip.com"
}

# 针对 GxLoader 的关键字高亮
DEFAULT_KEYWORDS = {
	"PASS": "\033[32m",              # Green
	"SUCCESS": "\033[32m",           # Green
	"FAIL": "\033[31m",              # Red
	"ERROR": "\033[31m",             # Red
	"PANIC": "\033[31m",             # Red
	"warning": "\033[33m",           # Yellow (警告)
	"no found": "\033[31m",          # Red (关键错误)
	"boot>": "\033[35m",             # Magenta (提示符)
	"Hit any key": "\033[36m",       # Cyan (交互提示)
}

COLOR_RESET = "\033[0m"
COLOR_TX = "\033[36m"     # Cyan
