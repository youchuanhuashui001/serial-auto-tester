# 专业 HTML 邮件模板实施计划

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** 实现一个结构化的 HTML 邮件模板，展示详细的测试信息、结果列表和工具签名。

**Architecture:** 
- **渲染器**: 新增 `renderer.py`，负责将元数据和结果列表转换为 HTML 字符串。
- **通知器**: 更新 `notifier.py` 支持发送 HTML 格式邮件。
- **核心逻辑**: 更新 `core.py` 支持在 `notify_user` 中动态接收元数据。

**Tech Stack:** Python 3, `email.mime.html`.

---

### Task 1: 实现 HTML 渲染器

**Files:**
- Create: `renderer.py`

**Step 1: 编写渲染逻辑**

```python
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
```

**Step 2: Commit**

```bash
git add renderer.py
git commit -m "feat: add HTML report renderer"
```

---

### Task 2: 升级 Notifier 以支持 HTML

**Files:**
- Modify: `notifier.py`

**Step 1: 修改 `send` 方法以支持 HTML 文本**

```python
# notifier.py 核心修改
def send(self, subject, content, attachment_path=None, is_html=True):
    # ... 前面代码保持不变 ...
    
    # 更改正文添加逻辑
    msg_type = 'html' if is_html else 'plain'
    message.attach(MIMEText(content, msg_type, 'utf-8'))
    
    # ... 后续代码保持不变 ...
```

**Step 2: Commit**

```bash
git commit -am "feat: update notifier to support HTML emails"
```

---

### Task 3: 在 SerialTester 中集成渲染逻辑

**Files:**
- Modify: `core.py`

**Step 1: 增加 `start_time` 记录并集成渲染器**

```python
# core.py
from renderer import ReportRenderer

class SerialTester:
    def __init__(self, ...):
        # ...
        self.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def notify_user(self, subject, results_list, attachment_path=None):
        """接收结果列表并渲染 HTML 发送"""
        metadata = {
            "start_time": self.start_time,
            "port": self.port,
            "baudrate": self.baudrate,
            "log_file": self.log_file
        }
        
        html_content = ReportRenderer.render(metadata, results_list)
        return self.notifier.send(subject, html_content, attachment_path, is_html=True)
```

**Step 2: Commit**

```bash
git commit -am "feat: integrate HTML renderer into SerialTester"
```

---

### Task 4: 更新测试用例以传递结构化数据

**Files:**
- Modify: `cases/flash_test.py`

**Step 1: 修改结果收集方式**

```python
# 现在的 results 是 [("UID", True, "msg"), ...]
# 需要转换为 [{"item": "Flash UID", "status": "PASS", "msg": "msg"}, ...]
formatted_results = []
for name, success, msg in results:
    formatted_results.append({
        "item": name,
        "status": "PASS" if success else "FAIL",
        "msg": msg
    })

tester.notify_user(subject, formatted_results, attachment_path=tester.log_file)
```

**Step 2: Commit**

```bash
git commit -am "feat: update flash_test to use structured results for HTML reporting"
```
