#!/usr/bin/env python3
"""
批量解压并上传到Hugging Face的脚本
每次处理10个文件夹，解压→上传→删除，节省空间
"""

import os
import sys
import zipfile
import tarfile
import shutil
import time
from pathlib import Path
from typing import List, Optional
from huggingface_hub import HfApi, login

class BatchUploader:
    def __init__(self,
                 archive_path: str,
                 repo_id: str,
                 temp_dir: str = "/tmp/hf_upload_temp",
                 batch_size: int = 10,
                 repo_type: str = "dataset",
                 token: Optional[str] = None):
        """
        初始化批量上传器

        Args:
            archive_path: 压缩包路径
            repo_id: Hugging Face仓库ID (格式: username/repo-name)
            temp_dir: 临时解压目录
            batch_size: 每批处理的文件夹数量
            repo_type: 仓库类型 ('dataset' 或 'model')
            token: Hugging Face token (可选，如果已登录则不需要)
        """
        self.archive_path = archive_path
        self.repo_id = repo_id
        self.temp_dir = temp_dir
        self.batch_size = batch_size
        self.repo_type = repo_type
        self.token = token

        # 创建临时目录
        os.makedirs(self.temp_dir, exist_ok=True)

        # 初始化HF API
        if self.token:
            login(token=self.token)
        self.api = HfApi()

        # 进度记录文件
        self.progress_file = Path(__file__).parent / "upload_progress.txt"

    def get_archive_members(self) -> List[str]:
        """获取压缩包中的所有顶层文件夹"""
        members = []

        # 验证文件存在
        if not os.path.exists(self.archive_path):
            raise FileNotFoundError(f"压缩包不存在: {self.archive_path}")

        # 验证文件可读
        if not os.access(self.archive_path, os.R_OK):
            raise PermissionError(f"无权限读取文件: {self.archive_path}")

        if self.archive_path.endswith('.zip'):
            try:
                # 使用 is_zipfile 检查
                if not zipfile.is_zipfile(self.archive_path):
                    raise ValueError(f"文件不是有效的 ZIP 格式: {self.archive_path}")

                with zipfile.ZipFile(self.archive_path, 'r', allowZip64=True) as zf:
                    all_names = zf.namelist()
            except zipfile.BadZipFile as e:
                raise ValueError(f"ZIP 文件损坏: {str(e)}")
        elif self.archive_path.endswith(('.tar.gz', '.tgz', '.tar')):
            with tarfile.open(self.archive_path, 'r:*') as tf:
                all_names = tf.getnames()
        else:
            raise ValueError("不支持的压缩格式。仅支持 .zip, .tar.gz, .tgz, .tar")

        # 提取顶层文件夹名称
        top_level = set()
        for name in all_names:
            parts = name.split('/')
            if parts[0] and parts[0] not in ['.', '..']:
                top_level.add(parts[0])

        # 筛选符合 s0000-s14XX 模式的文件夹
        members = sorted([m for m in top_level if m.startswith('s') and len(m) == 5])

        print(f"找到 {len(members)} 个符合模式的文件夹")
        return members

    def load_progress(self) -> set:
        """加载已上传的文件夹列表"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return set(line.strip() for line in f if line.strip())
        return set()

    def save_progress(self, folder_name: str):
        """保存上传进度"""
        with open(self.progress_file, 'a') as f:
            f.write(f"{folder_name}\n")

    def extract_folder(self, folder_name: str) -> Path:
        """从压缩包中提取指定文件夹"""
        extract_path = Path(self.temp_dir) / folder_name

        if self.archive_path.endswith('.zip'):
            with zipfile.ZipFile(self.archive_path, 'r', allowZip64=True) as zf:
                # 提取所有以该文件夹名开头的文件
                members = [m for m in zf.namelist() if m.startswith(folder_name + '/') or m == folder_name]
                zf.extractall(self.temp_dir, members=members)
        else:
            with tarfile.open(self.archive_path, 'r:*') as tf:
                members = [m for m in tf.getmembers() if m.name.startswith(folder_name + '/') or m.name == folder_name]
                tf.extractall(self.temp_dir, members=members)

        return extract_path

    def upload_folder(self, folder_path: Path, folder_name: str):
        """上传文件夹到Hugging Face"""
        print(f"  正在上传 {folder_name} 到 {self.repo_id}...")

        try:
            self.api.upload_folder(
                folder_path=str(folder_path),
                path_in_repo=folder_name,
                repo_id=self.repo_id,
                repo_type=self.repo_type,
                multi_commits=True,
                multi_commits_verbose=True
            )
            print(f"  ✓ {folder_name} 上传成功")
            return True
        except Exception as e:
            print(f"  ✗ {folder_name} 上传失败: {str(e)}")
            return False

    def cleanup_folder(self, folder_path: Path):
        """删除临时文件夹"""
        if folder_path.exists():
            shutil.rmtree(folder_path)

    def run(self):
        """运行批量上传流程"""
        print("=" * 60)
        print(f"开始批量上传任务")
        print(f"压缩包: {self.archive_path}")
        print(f"目标仓库: {self.repo_id}")
        print(f"每批数量: {self.batch_size}")
        print("=" * 60)

        # 获取所有文件夹
        all_folders = self.get_archive_members()

        # 加载进度
        uploaded = self.load_progress()
        remaining = [f for f in all_folders if f not in uploaded]

        if not remaining:
            print("\n所有文件夹已上传完成！")
            return

        print(f"\n已完成: {len(uploaded)}/{len(all_folders)}")
        print(f"待处理: {len(remaining)}/{len(all_folders)}")
        print()

        # 分批处理
        total_batches = (len(remaining) + self.batch_size - 1) // self.batch_size

        for batch_num in range(total_batches):
            start_idx = batch_num * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(remaining))
            batch = remaining[start_idx:end_idx]

            print(f"\n[批次 {batch_num + 1}/{total_batches}] 处理 {len(batch)} 个文件夹")
            print("-" * 60)

            for i, folder_name in enumerate(batch, 1):
                print(f"\n[{start_idx + i}/{len(remaining)}] 处理: {folder_name}")

                try:
                    # 1. 解压
                    print(f"  正在解压 {folder_name}...")
                    folder_path = self.extract_folder(folder_name)

                    if not folder_path.exists():
                        print(f"  ✗ 解压失败: 文件夹不存在")
                        continue

                    # 2. 上传
                    success = self.upload_folder(folder_path, folder_name)

                    # 3. 删除临时文件
                    if success:
                        print(f"  正在清理临时文件...")
                        self.cleanup_folder(folder_path)
                        self.save_progress(folder_name)
                        print(f"  ✓ {folder_name} 处理完成")
                    else:
                        print(f"  ! 保留临时文件以便重试: {folder_path}")

                except Exception as e:
                    print(f"  ✗ 处理 {folder_name} 时出错: {str(e)}")
                    continue

                # 短暂休息，避免API限流
                time.sleep(1)

            print(f"\n批次 {batch_num + 1} 完成")
            print("=" * 60)

        print(f"\n🎉 所有批次处理完成！")
        print(f"查看您的数据集: https://huggingface.co/{self.repo_id}")


def main():
    """主函数"""
    # 配置参数 - 请修改这些参数
    ARCHIVE_PATH = "/path/to/your/archive.zip"  # 压缩包路径
    REPO_ID = "your-username/your-repo-name"     # HF仓库ID
    TEMP_DIR = "/tmp/hf_upload_temp"             # 临时目录
    BATCH_SIZE = 10                               # 每批处理数量
    REPO_TYPE = "dataset"                         # 仓库类型: 'dataset' 或 'model'
    HF_TOKEN = None                               # HF token (可选，如果已通过 huggingface-cli login 登录)

    # 参数验证
    if not os.path.exists(ARCHIVE_PATH):
        print(f"错误: 找不到压缩包文件: {ARCHIVE_PATH}")
        print("请在脚本中设置正确的 ARCHIVE_PATH")
        sys.exit(1)

    if REPO_ID == "your-username/your-repo-name":
        print("错误: 请设置正确的 REPO_ID")
        print("格式: username/repo-name")
        sys.exit(1)

    # 创建上传器并运行
    uploader = BatchUploader(
        archive_path=ARCHIVE_PATH,
        repo_id=REPO_ID,
        temp_dir=TEMP_DIR,
        batch_size=BATCH_SIZE,
        repo_type=REPO_TYPE,
        token=HF_TOKEN
    )

    try:
        uploader.run()
    except KeyboardInterrupt:
        print("\n\n用户中断，进度已保存。")
        print("再次运行脚本将从上次中断的地方继续。")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
