#!/usr/bin/env python3
"""
运行脚本 - 使用 config.py 中的配置运行批量上传
"""

import sys
import os

# 导入配置
from config import (
    ARCHIVE_PATH,
    REPO_ID,
    TEMP_DIR,
    BATCH_SIZE,
    REPO_TYPE,
    HF_TOKEN
)

# 导入主程序
from batch_upload import BatchUploader


def main():
    """主函数"""
    # 参数验证
    if not os.path.exists(ARCHIVE_PATH):
        print(f"❌ 错误: 找不到压缩包文件: {ARCHIVE_PATH}")
        print("请在 config.py 中设置正确的 ARCHIVE_PATH")
        sys.exit(1)

    if REPO_ID == "your-username/your-repo-name":
        print("❌ 错误: 请在 config.py 中设置正确的 REPO_ID")
        print("格式: username/repo-name")
        sys.exit(1)

    print("\n配置信息:")
    print(f"  压缩包: {ARCHIVE_PATH}")
    print(f"  目标仓库: {REPO_ID}")
    print(f"  临时目录: {TEMP_DIR}")
    print(f"  批次大小: {BATCH_SIZE}")
    print(f"  仓库类型: {REPO_TYPE}")
    print()

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
        print("\n\n⚠️  用户中断，进度已保存。")
        print("再次运行脚本将从上次中断的地方继续。")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
