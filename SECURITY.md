# 安全配置指南

## Token 安全管理

为了避免将敏感的 Hugging Face token 提交到 GitHub，我们使用了以下方案：

### 方案结构

```
unzip_ser/
├── config.py              # 公开配置（token = None）
├── secrets.py             # 私密配置（包含真实 token，已被 gitignore）
├── secrets.py.example     # 示例文件（可以提交到 git）
├── .gitignore             # 忽略 secrets.py
└── run.py                 # 自动从 secrets.py 读取 token
```

### 使用方法

#### 方法 1: 使用 secrets.py（推荐）

1. **复制示例文件**：
   ```bash
   cp secrets.py.example secrets.py
   ```

2. **编辑 secrets.py**：
   ```python
   HF_TOKEN = "hf_YOUR_ACTUAL_TOKEN_HERE"
   ```

3. **运行程序**：
   ```bash
   python run.py
   # 会自动从 secrets.py 读取 token
   ```

#### 方法 2: 使用命令行登录

```bash
huggingface-cli login
# 输入您的 token，会被安全保存
```

然后运行程序，无需在代码中配置 token。

#### 方法 3: 使用环境变量

```bash
export HF_TOKEN="hf_YOUR_TOKEN_HERE"
python run.py
```

### Git 提交检查清单

在提交代码到 GitHub 前，请确保：

- [ ] `secrets.py` 已被 `.gitignore` 忽略
- [ ] `config.py` 中 `HF_TOKEN = None`
- [ ] 没有在其他文件中硬编码 token

### 检查是否泄露 token

```bash
# 检查 git 历史中是否有 token
git log -p | grep -i "hf_"

# 检查当前文件
grep -r "hf_[A-Za-z0-9]" --exclude-dir=venv --exclude=secrets.py .
```

### 如果 token 已经泄露

1. **立即撤销 token**：
   - 访问 https://huggingface.co/settings/tokens
   - 删除泄露的 token

2. **创建新 token**：
   - 生成新的 token
   - 更新 `secrets.py`

3. **清理 git 历史**（如果已提交）：
   ```bash
   # 使用 git filter-branch 或 BFG Repo-Cleaner
   # 详见: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
   ```

### 服务器部署

在服务器上部署时：

1. **设置文件权限**：
   ```bash
   chmod 600 secrets.py
   ```

2. **或使用环境变量**：
   ```bash
   # 添加到 ~/.bashrc
   export HF_TOKEN="hf_YOUR_TOKEN_HERE"
   ```

## 最佳实践

1. ✅ **永远不要**将 token 硬编码到可能被提交的文件中
2. ✅ **使用** `.gitignore` 排除敏感文件
3. ✅ **定期轮换** token
4. ✅ **限制 token 权限**（只给必要的权限）
5. ✅ **使用不同的 token** 用于开发和生产环境
