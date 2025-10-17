# 批量解压上传到 Hugging Face 工具

这个工具可以帮助您在存储空间有限的服务器上，分批次地从压缩包中解压文件夹并上传到 Hugging Face，避免一次性解压导致空间不足。

## 功能特点

- 分批处理：每次处理 10 个文件夹（可配置）
- 节省空间：解压→上传→删除，循环处理
- 断点续传：支持中断后继续，进度自动保存
- 自动筛选：自动识别 s0000-s14XX 格式的文件夹
- 错误处理：单个文件夹失败不影响其他文件夹

## 环境要求

```bash
pip install huggingface_hub
```

## 使用步骤

### 1. 配置参数

编辑 `config.py` 文件，修改以下必填参数：

```python
# 压缩包的完整路径
ARCHIVE_PATH = "/path/to/your/archive.zip"

# Hugging Face 仓库 ID
REPO_ID = "your-username/your-repo-name"
```

可选参数（根据需要调整）：

```python
TEMP_DIR = "/tmp/hf_upload_temp"  # 临时目录
BATCH_SIZE = 10                    # 每批处理数量
REPO_TYPE = "dataset"              # 仓库类型
HF_TOKEN = None                    # HF Token（可选）
```

### 2. 登录 Hugging Face

```bash
huggingface-cli login
```

输入您的 token（从 https://huggingface.co/settings/tokens 获取）

### 3. 创建目标仓库

在 Hugging Face 上创建一个仓库：
- 访问 https://huggingface.co/new-dataset （如果是数据集）
- 或 https://huggingface.co/new （如果是模型）
- 创建仓库后记下仓库 ID（例如：username/repo-name）

### 4. 运行脚本

```bash
cd /home/zhanghaochen/Desktop/cours/TDSI/unzip_ser
python3 run.py
```

## 工作流程

```
[压缩包]
   ↓
[解压批次1: s0000-s0009] → [上传到HF] → [删除临时文件]
   ↓
[解压批次2: s0010-s0019] → [上传到HF] → [删除临时文件]
   ↓
[解压批次3: s0020-s0029] → [上传到HF] → [删除临时文件]
   ↓
   ...
```

## 断点续传

如果上传过程被中断（Ctrl+C 或网络问题）：

1. 进度会自动保存在 `upload_progress.txt`
2. 再次运行 `python3 run.py` 会自动跳过已上传的文件夹
3. 从上次中断的地方继续

## 查看进度

运行过程中会显示：

```
[批次 1/145] 处理 10 个文件夹
--------------------------------------------------

[1/1450] 处理: s0000
  正在解压 s0000...
  正在上传 s0000 到 username/repo-name...
  ✓ s0000 上传成功
  正在清理临时文件...
  ✓ s0000 处理完成
```

## 目录结构

```
unzip_ser/
├── batch_upload.py      # 核心上传逻辑
├── config.py            # 配置文件（需要修改）
├── run.py               # 运行入口
├── README.md            # 使用说明
└── upload_progress.txt  # 进度记录（自动生成）
```

## 注意事项

### 空间要求

确保临时目录至少有足够空间容纳 `BATCH_SIZE` 个文件夹的大小。例如：
- 如果每个文件夹 1GB
- BATCH_SIZE = 10
- 需要至少 10-15GB 临时空间

### 调整批次大小

如果空间紧张，可以减少 `BATCH_SIZE`：

```python
BATCH_SIZE = 5  # 或更小
```

### 支持的压缩格式

- `.zip`
- `.tar.gz`
- `.tgz`
- `.tar`

### 网络中断处理

如果网络不稳定导致上传失败：
1. 脚本会保留失败文件夹的临时文件
2. 检查错误信息
3. 修复问题后重新运行脚本

## 示例配置

### 示例 1：上传数据集

```python
# config.py
ARCHIVE_PATH = "/data/dataset.zip"
REPO_ID = "myusername/my-dataset"
TEMP_DIR = "/tmp/upload_temp"
BATCH_SIZE = 10
REPO_TYPE = "dataset"
```

### 示例 2：空间受限

```python
# config.py
ARCHIVE_PATH = "/data/large_archive.tar.gz"
REPO_ID = "myusername/my-repo"
TEMP_DIR = "/tmp/small_temp"
BATCH_SIZE = 3  # 一次只处理3个
REPO_TYPE = "dataset"
```

## 常见问题

### Q: 如何查看已上传了哪些文件夹？

A: 查看 `upload_progress.txt` 文件：

```bash
cat upload_progress.txt
```

### Q: 如何重新上传某个文件夹？

A: 从 `upload_progress.txt` 中删除对应行，重新运行脚本。

### Q: 上传速度慢怎么办？

A: 这是正常现象，取决于：
- 网络速度
- 文件大小
- Hugging Face 服务器状态

### Q: 可以并行上传吗？

A: 当前版本为顺序上传，确保稳定性和空间可控。

## 许可证

MIT License

## 技术支持

如有问题，请检查：
1. 配置是否正确
2. 网络连接是否正常
3. Hugging Face token 是否有效
4. 临时目录是否有足够空间
# loae_the_data
