# 邮件报告模板设计文档 (2026-03-04)

## 1. 目标 (Goal)
设计一个专业、简洁、结构化的 HTML 邮件模板，用于展示串口自动化测试的概览和结果。
支持：
- 自动抓取并展示测试元数据（时间、串口、参数）。
- 格式整齐的测试项结果表格。
- 固定风格的工具信息签名。

## 2. 核心组件 (Components)

### A. 模板渲染器 (`TemplateHandler`)
- 职责：接收测试数据（元数据、结果列表），将其填充到 HTML 字符串中。
- 输入数据格式：
  ```python
  metadata = {
      "start_time": "2026-03-04 20:00:00",
      "port": "/dev/ttyUSB0",
      "baudrate": 115200,
      "log_file": "logs/test.log"
  }
  results = [
      {"item": "UID", "status": "PASS", "msg": "Passed"},
      ...
  ]
  ```

### B. 邮件发送器集成 (`notifier.py`)
- 更新 `send` 方法：支持 `MIMEText(html, 'html')`。

## 3. HTML 结构设计 (HTML Structure)
采用基础 HTML 标签（兼容性最佳）：
- **容器**: `<div>` 居中，最大宽度 800px。
- **元数据**: 使用 `<ul>` 或简单的 `<div>` 堆叠，带有加粗的标签。
- **结果表**: 使用 `<table>`，带细灰色边框，内边距 8px。
- **签名**: 使用 `<p style="text-align: right; font-style: italic;">`。

## 4. 视觉规范 (Style)
- **字体**: 系统默认无衬线字体 (sans-serif)。
- **颜色**: 纯黑白风格，不带高亮色。
- **对齐**: 文字左对齐，签名右对齐。

## 5. 异常处理
- 渲染失败时回退到纯文本模式，确保通知不中断。
