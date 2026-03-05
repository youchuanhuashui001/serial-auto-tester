# serial-auto-tester

基于 Python 的串口自动化测试辅助工具，支持实时日志记录、终端颜色区分、自动进入 Bootloader、Flash OTP/WP 专项测试及邮件通知。

## 快速开始
1. 安装依赖: `pip3 install -r requirements.txt`
2. 修改 `config.py` 配置串口和邮件信息
3. 运行测试: `python3 run.py flash_test`
