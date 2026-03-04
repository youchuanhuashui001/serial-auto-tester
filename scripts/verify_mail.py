from notifier import EmailNotifier
from config import MAIL_CONFIG

def test():
    notifier = EmailNotifier(MAIL_CONFIG)
    print("正在尝试发送测试邮件...")
    success = notifier.send("自动化测试连接成功", "这是一条来自 Ubuntu 串口测试工具的验证邮件。")
    if success:
        print("验证通过！请检查您的收件箱。")
    else:
        print("发送失败，请检查 config.py 中的授权码和服务器配置。")

if __name__ == "__main__":
    test()

