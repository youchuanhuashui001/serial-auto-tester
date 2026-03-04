# 串口自动化测试辅助工具实施计划

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** 构建一个基于 Python 的多线程串口自动化测试类库，支持实时日志记录、颜色区分和邮件通知。

**Architecture:** 
- **核心逻辑**: 使用 `pyserial` 处理底层通信。
- **并发处理**: 采用 `threading` 实现后台持续监听。
- **输出处理**: 使用 ANSI 转义码实现终端彩色高亮。
- **通知系统**: 基于 `smtplib` 的 SMTP 客户端。

**Tech Stack:** Python 3.8+, `pyserial`.

---

### Task 1: 项目基础结构与配置

**Files:**
- Create: `config.py`
- Create: `requirements.txt`

**Step 1: 创建配置文件模板**

```python
# config.py
SERIAL_CONFIG = {
    "port": "/dev/ttyUSB0",
    "baudrate": 115200,
    "timeout": 1
}

MAIL_CONFIG = {
    "smtp_server": "smtp.example.com",
    "smtp_port": 465,
    "sender": "your_email@example.com",
    "password": "your_auth_code",
    "receiver": "receiver@example.com"
}

DEFAULT_KEYWORDS = {
    "PASS": "\033[32m",    # Green
    "SUCCESS": "\033[32m", # Green
    "FAIL": "\033[31m",    # Red
    "ERROR": "\033[31m",   # Red
    "PANIC": "\033[31m",   # Red
}

COLOR_RESET = "\033[0m"
COLOR_TX = "\033[36m"     # Cyan
```

**Step 2: 创建依赖文件**

```text
pyserial>=3.4
```

**Step 3: 安装依赖**

Run: `pip3 install -r requirements.txt`

**Step 4: Commit**

```bash
git add config.py requirements.txt
git commit -m "chore: initial project structure and config"
```

---

### Task 2: 核心串口类 SerialTester (基础读写)

**Files:**
- Create: `core.py`
- Create: `tests/test_core_basic.py`

**Step 1: 编写基础连接测试**

```python
import unittest
from core import SerialTester

class TestSerialBasic(unittest.TestCase):
    def test_init(self):
        tester = SerialTester(port="/dev/ttyUSB0")
        self.assertEqual(tester.port, "/dev/ttyUSB0")
```

**Step 2: 实现 SerialTester 类骨架**

```python
import serial
import threading
import time
from datetime import datetime

class SerialTester:
    def __init__(self, port, baudrate=115200, log_file=None):
        self.port = port
        self.baudrate = baudrate
        self.log_file = log_file or f"serial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.ser = None
        self.is_running = False
        self.reader_thread = None
        self.keywords = {}

    def start(self):
        self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
        self.is_running = True
        self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.reader_thread.start()

    def _read_loop(self):
        with open(self.log_file, "a") as f:
            while self.is_running:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8', errors='ignore')
                    if line:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        # 基础处理逻辑...
                        print(f"[{timestamp}] [RX] << {line.strip()}")
                        f.write(f"[{timestamp}] [RX] << {line}")
                        f.flush()
                time.sleep(0.01)

    def stop(self):
        self.is_running = False
        if self.reader_thread:
            self.reader_thread.join()
        if self.ser:
            self.ser.close()
```

**Step 3: 运行测试验证**

Run: `python3 -m unittest tests/test_core_basic.py`
Expected: PASS

**Step 4: Commit**

```bash
git add core.py tests/test_core_basic.py
git commit -m "feat: implement basic SerialTester class with read loop"
```

---

### Task 3: 颜色处理与关键字高亮

**Files:**
- Modify: `core.py`

**Step 1: 实现颜色渲染逻辑**

```python
    def set_keywords(self, kw_dict):
        self.keywords = kw_dict

    def _apply_colors(self, text):
        reset = "\033[0m"
        for word, color_code in self.keywords.items():
            if word in text:
                text = text.replace(word, f"{color_code}{word}{reset}")
        return text

    def send_cmd(self, cmd):
        if not cmd.endswith("\n"):
            cmd += "\n"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        cyan = "\033[36m"
        reset = "\033[0m"
        print(f"{cyan}[{timestamp}] [TX] >> {cmd.strip()}{reset}")
        
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] [TX] >> {cmd}")
            f.flush()
            
        self.ser.write(cmd.encode())
```

**Step 2: 更新 `_read_loop` 调用颜色处理**

```python
    # 在 _read_loop 中修改打印行
    colored_line = self._apply_colors(line.strip())
    print(f"[{timestamp}] [RX] << {colored_line}")
```

**Step 3: Commit**

```bash
git commit -am "feat: add color highlighting and command sending"
```

---

### Task 4: 邮件通知模块

**Files:**
- Create: `notifier.py`

**Step 1: 实现 EmailNotifier 类**

```python
import smtplib
from email.mime.text import MIMEText
from email.header import Header

class EmailNotifier:
    def __init__(self, config):
        self.config = config

    def send(self, subject, content):
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = self.config['sender']
        message['To'] = self.config['receiver']
        message['Subject'] = Header(subject, 'utf-8')

        try:
            with smtplib.SMTP_SSL(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.login(self.config['sender'], self.config['password'])
                server.sendmail(self.config['sender'], [self.config['receiver']], message.as_string())
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
```

**Step 2: 在 SerialTester 中集成**

```python
    def notify_user(self, subject, content):
        from notifier import EmailNotifier
        from config import MAIL_CONFIG
        notifier = EmailNotifier(MAIL_CONFIG)
        return notifier.send(subject, content)
```

**Step 3: Commit**

```bash
git add notifier.py
git commit -am "feat: integrate email notification"
```

---

### Task 5: 示例用例与最终验证

**Files:**
- Create: `example_case.py`

**Step 1: 编写演示用例**

```python
from core import SerialTester
from config import SERIAL_CONFIG, DEFAULT_KEYWORDS
import time

def run_test():
    tester = SerialTester(SERIAL_CONFIG['port'], SERIAL_CONFIG['baudrate'])
    tester.set_keywords(DEFAULT_KEYWORDS)
    
    print("Starting Serial Automation Tool...")
    tester.start()
    
    # 示例交互
    tester.send_cmd("help")
    time.sleep(2)
    
    tester.send_cmd("uname -a")
    time.sleep(1)
    
    # 模拟检测到成功或失败
    print("\n--- Manual Check Simulation ---")
    result = input("Did the test pass? (y/n): ")
    
    if result.lower() == 'y':
        tester.notify_user("Test Report: PASS", "The automation test case finished successfully.")
    else:
        tester.notify_user("Test Report: FAIL", "The automation test case failed at step 2.")
        
    tester.stop()
    print("Done. Log saved to:", tester.log_file)

if __name__ == "__main__":
    run_test()
```

**Step 2: Commit**

```bash
git add example_case.py
git commit -m "feat: add example test case"
```
