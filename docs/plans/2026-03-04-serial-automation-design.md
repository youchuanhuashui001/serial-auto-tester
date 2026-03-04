# 串口自动化测试辅助工具设计文档 (2026-03-04)

## 1. 目标 (Goal)
构建一个基于 Python 的串口测试类库，用于 Ubuntu 20.04 环境下的自动化测试。
支持：
- 实时监听串口，异步读写分离。
- 日志文件自动记录（带时间戳）。
- 终端彩色显示（区分 TX/RX 内容及关键字高亮）。
- 手动触发邮件通知。

## 2. 系统架构 (Architecture)
采用 **多线程异步监听模型**：
- **主线程 (Main Thread)**: 执行测试逻辑 (Python API 调用)。
- **读线程 (Read Thread)**: 持续监控串口输入，处理颜色过滤，写入日志文件。

### 核心组件
- `SerialTester`: 核心类，封装串口读写。
- `OutputHandler`: 负责终端颜色和日志文件格式。
- `EmailNotifier`: 负责 SMTP 邮件发送逻辑。

## 3. API 接口定义 (API Definition)

| 方法名 | 说明 |
| :--- | :--- |
| `__init__(port, baudrate, log_file)` | 初始化串口参数及日志文件。 |
| `start()` | 启动串口监听线程。 |
| `stop()` | 关闭串口并停止线程。 |
| `send_cmd(cmd)` | 发送指令，控制台显示为青色并带 `[TX] >>` 前缀。 |
| `set_keywords(kw_dict)` | 设置高亮关键字字典。如 `{"PASS": "green", "FAIL": "red"}`。 |
| `notify_user(subject, content)` | 手动触发邮件通知。 |

## 4. 终端显示规范 (Terminal Display)
- **TX 内容**: `[2026-03-04 10:00:00.123] [TX] >> cmd_string` (青色高亮)
- **RX 内容**: `[2026-03-04 10:00:00.456] [RX] << log_content` (默认色)
- **关键字匹配**: 自动将 `log_content` 中的关键字替换为对应的 ANSI 颜色代码。

## 5. 日志文件规范 (Logging)
- 文件名默认：`serial_log_YYYYMMDD_HHMMSS.log`。
- 格式：纯文本，带 `[TX]/[RX]` 标签，方便后续用 `grep` 过滤。

## 6. 邮件通知 (Notification)
- 使用 `smtplib` 配合授权码。
- 配置项将放在 `config.py` 中。

## 7. 异常处理
- 串口断开重连尝试。
- 线程安全地关闭资源。
- 邮件发送失败不阻塞主流程。
