#!/bin/bash
# 自动设置虚拟环境并运行上传脚本

set -e  # 遇到错误立即退出

echo "=================================="
echo "Hugging Face 批量上传工具"
echo "=================================="
echo

# 虚拟环境目录
VENV_DIR="venv"

# 检查虚拟环境是否存在
if [ ! -d "$VENV_DIR" ]; then
    echo "首次运行：正在创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
    echo "✓ 虚拟环境创建完成"
    echo
fi

# 激活虚拟环境
echo "正在激活虚拟环境..."
source "$VENV_DIR/bin/activate"
echo "✓ 虚拟环境已激活"
echo

# 检查是否需要安装依赖
if ! "$VENV_DIR/bin/python" -c "import huggingface_hub" 2>/dev/null; then
    echo "正在安装依赖包..."
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install huggingface_hub
    echo "✓ 依赖包安装完成"
    echo
else
    echo "✓ 依赖包已安装"
    echo
fi

# 运行主程序
echo "开始运行上传脚本..."
echo "=================================="
echo
"$VENV_DIR/bin/python" run.py

# 脚本结束
echo
echo "=================================="
echo "脚本执行完成"
echo "=================================="
