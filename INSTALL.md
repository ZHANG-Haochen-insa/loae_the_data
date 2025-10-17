# 服务器安装和使用指南

## 问题说明

服务器使用了系统管理的 Python 环境，不允许直接使用 `pip install`。需要使用虚拟环境。

## 解决方案

我们提供了自动化脚本 `setup_and_run.sh`，它会自动：
1. 创建虚拟环境
2. 安装依赖
3. 运行上传程序

## 使用步骤

### 1. 上传文件到服务器

在本地运行：
```bash
scp -r /home/zhanghaochen/Desktop/cours/TDSI/unzip_ser hzhang02@anchiale14:~/TDSI-2025/b04/
```

### 2. SSH 连接到服务器

```bash
ssh hzhang02@anchiale14
```

### 3. 进入目录

```bash
cd ~/TDSI-2025/b04/unzip_ser
```

### 4. 运行脚本（一键完成）

```bash
./setup_and_run.sh
```

**首次运行**会自动：
- 创建虚拟环境（venv 文件夹）
- 安装 huggingface_hub
- 开始上传数据

**后续运行**会直接开始上传，无需重新安装。

## 中断和继续

- **中断上传**：按 `Ctrl+C`
- **继续上传**：再次运行 `./setup_and_run.sh`
- 进度自动保存在 `upload_progress.txt`

## 手动方式（如果需要）

如果自动脚本有问题，可以手动执行：

```bash
# 1. 创建虚拟环境
python3 -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装依赖
pip install huggingface_hub

# 4. 运行程序
python run.py

# 5. 退出虚拟环境（完成后）
deactivate
```

## 检查进度

查看已上传的文件夹：
```bash
cat upload_progress.txt
```

查看还有多少文件夹待上传：
```bash
wc -l upload_progress.txt
```

## 空间不足时

如果 `/tmp` 空间不够，可以修改 `config.py` 中的 `TEMP_DIR`：
```python
TEMP_DIR = "/home/hzhang02/tmp_upload"  # 使用自己目录下的空间
```

或者减少批次大小：
```python
BATCH_SIZE = 5  # 从 10 改为 5
```

## 故障排查

### 错误：No space left on device
- 修改 `TEMP_DIR` 到空间更大的目录
- 减少 `BATCH_SIZE`

### 错误：Permission denied
- 确保脚本有执行权限：`chmod +x setup_and_run.sh`

### 错误：Module not found
- 确保在虚拟环境中运行
- 重新安装：`source venv/bin/activate && pip install huggingface_hub`
