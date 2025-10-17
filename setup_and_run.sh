#!/bin/bash
# 自动设置虚拟环境并运行上传脚本

echo "=================================="
echo "Hugging Face 批量上传工具"
echo "=================================="
echo

# 虚拟环境目录
VENV_DIR="venv"

# 检查 python3-venv 是否可用
echo "检查系统依赖..."
if ! python3 -m venv --help > /dev/null 2>&1; then
    echo "错误: python3-venv 未安装"
    echo "请运行以下命令安装:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install python3-venv python3-pip"
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d "$VENV_DIR" ]; then
    echo "首次运行：正在创建虚拟环境..."
    python3 -m venv "$VENV_DIR" --system-site-packages
    if [ $? -ne 0 ]; then
        echo "错误: 虚拟环境创建失败"
        echo "尝试不使用 --system-site-packages 选项..."
        python3 -m venv "$VENV_DIR"
    fi
    echo "✓ 虚拟环境创建完成"
    echo
fi

# 激活虚拟环境
echo "正在激活虚拟环境..."
source "$VENV_DIR/bin/activate"
echo "✓ 虚拟环境已激活"
echo "Python 路径: $(which python)"
echo

# 检查是否需要安装依赖
if ! python -c "import huggingface_hub" 2>/dev/null; then
    echo "正在安装依赖包..."
    python -m pip install --upgrade pip
    python -m pip install huggingface_hub
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
python run.py

# 脚本结束
echo
echo "=================================="
echo "脚本执行完成"
echo "=================================="
