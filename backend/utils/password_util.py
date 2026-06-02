"""
密码工具模块
使用 bcrypt 算法进行密码哈希和验证
兼容 bcrypt 4.x 和 5.x 版本
"""
import bcrypt


def hash_password(plain_password: str) -> str:
    """
    对明文密码进行bcrypt哈希
    :param plain_password: 明文密码, 如 "admin123"
    :return: bcrypt哈希字符串
    """
    password_bytes = plain_password.encode('utf-8')
    # 如果密码超过72字节则截断（bcrypt限制）
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码是否与哈希匹配
    :param plain_password: 用户输入的明文密码
    :param hashed_password: 数据库中存储的哈希密码
    :return: True=匹配, False=不匹配
    """
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)
