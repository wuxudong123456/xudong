"""
密码工具模块
使用 bcrypt 算法进行密码哈希和验证
"""
from passlib.context import CryptContext

# 配置bcrypt加密上下文
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # 加密轮数，平衡安全性与性能
)


def hash_password(plain_password: str) -> str:
    """
    对明文密码进行bcrypt哈希
    :param plain_password: 明文密码, 如 "123456"
    :return: bcrypt哈希字符串, 如 "$2b$12$..."
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码是否与哈希匹配
    :param plain_password: 用户输入的明文密码
    :param hashed_password: 数据库中存储的哈希密码
    :return: True=匹配, False=不匹配
    """
    return pwd_context.verify(plain_password, hashed_password)
