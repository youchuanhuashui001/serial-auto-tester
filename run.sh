#!/bin/bash
# ===========================================================
# serial-auto-tester 测试启动脚本
# 用法: 取消注释需要执行的测试项，然后运行 ./run.sh
# ===========================================================

cd "$(dirname "$0")"

# ---------------------------------------------------------
# 测试项列表 (注释掉不需要测试的项)
# ---------------------------------------------------------

python3 run.py flash_test
# python3 run.py boot_test
# python3 run.py uart_test
# python3 run.py i2c_test
# python3 run.py spi_test
# python3 run.py gpio_test
