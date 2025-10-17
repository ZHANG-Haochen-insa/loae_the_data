"""
配置文件 - 请根据您的实际情况修改这些参数
"""

# ==================== 必填配置 ====================

# 压缩包的完整路径
ARCHIVE_PATH = "/path/to/your/archive.zip"

# Hugging Face 仓库 ID (格式: username/repo-name)
# 例如: "zhangsan/my-dataset"
REPO_ID = "your-username/your-repo-name"


# ==================== 可选配置 ====================

# 临时解压目录 (确保有足够空间容纳10个文件夹)
TEMP_DIR = "/tmp/hf_upload_temp"

# 每批处理的文件夹数量 (根据可用空间调整)
BATCH_SIZE = 10

# 仓库类型: "dataset" 或 "model"
REPO_TYPE = "dataset"

# Hugging Face Token (如果已通过 huggingface-cli login 登录则无需填写)
# 获取token: https://huggingface.co/settings/tokens
HF_TOKEN = None
