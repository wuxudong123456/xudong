"""
密码迁移脚本
将现有明文密码批量迁移为bcrypt哈希
运行方式: python -m scripts.hash_passwords
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.entity.user import User
from backend.utils.password_util import hash_password, verify_password


def migrate_passwords():
    """将明文密码迁移为bcrypt哈希"""
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_deleted == 0).all()
        migrated_count = 0

        for user in users:
            # 如果密码不是bcrypt格式($2b$开头)，则进行哈希
            if not user.password.startswith("$2"):
                print(f"[迁移] 用户 {user.username} 密码从明文 → bcrypt哈希")
                user.password = hash_password(user.password)
                migrated_count += 1

        db.commit()
        print(f"\n密码迁移完成! 共迁移 {migrated_count} 个用户")
        print(f"所有密码已使用bcrypt加密存储")

    finally:
        db.close()


if __name__ == "__main__":
    migrate_passwords()
