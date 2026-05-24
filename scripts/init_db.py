"""
数据库初始化脚本
执行现有建表SQL + 新增表 + 初始化权限数据
运行方式: python -m scripts.init_db
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, SessionLocal
from backend.entity.base import Base
from backend.entity.permission import Permission, RolePermission
from backend.entity.user import User
from backend.utils.password_util import hash_password


def init_database():
    """初始化数据库：创建所有表 + 插入基础权限数据"""
    print("=" * 50)
    print("开始初始化数据库...")

    # 1. 创建所有实体对应的数据库表
    Base.metadata.create_all(bind=engine)
    print("[OK] 所有数据表创建完成")

    # 2. 初始化RBAC权限数据
    db = SessionLocal()
    try:
        # 插入默认权限 (如果不存在)
        permissions_data = [
            # 模块: 学生管理
            {"code": "student:view", "name": "查看学生", "module": "student"},
            {"code": "student:create", "name": "新增学生", "module": "student"},
            {"code": "student:update", "name": "编辑学生", "module": "student"},
            {"code": "student:delete", "name": "删除学生", "module": "student"},
            {"code": "student:import", "name": "导入学生", "module": "student"},
            {"code": "student:export", "name": "导出学生", "module": "student"},
            # 模块: 班级管理
            {"code": "class:view", "name": "查看班级", "module": "class"},
            {"code": "class:create", "name": "新增班级", "module": "class"},
            {"code": "class:update", "name": "编辑班级", "module": "class"},
            {"code": "class:delete", "name": "删除班级", "module": "class"},
            # 模块: 成绩管理
            {"code": "score:view", "name": "查看成绩", "module": "score"},
            {"code": "score:create", "name": "录入成绩", "module": "score"},
            {"code": "score:update", "name": "编辑成绩", "module": "score"},
            {"code": "score:delete", "name": "删除成绩", "module": "score"},
            {"code": "score:import", "name": "导入成绩", "module": "score"},
            # 模块: 就业管理
            {"code": "employment:view", "name": "查看就业", "module": "employment"},
            {"code": "employment:create", "name": "新增就业", "module": "employment"},
            {"code": "employment:update", "name": "编辑就业", "module": "employment"},
            {"code": "employment:delete", "name": "删除就业", "module": "employment"},
            # 模块: 课程管理
            {"code": "course:view", "name": "查看课程", "module": "course"},
            {"code": "course:create", "name": "新增课程", "module": "course"},
            {"code": "course:update", "name": "编辑课程", "module": "course"},
            {"code": "course:delete", "name": "删除课程", "module": "course"},
            # 模块: 仪表盘
            {"code": "dashboard:view", "name": "查看仪表盘", "module": "dashboard"},
            # 模块: 日志
            {"code": "log:view", "name": "查看操作日志", "module": "log"},
            # 模块: 系统管理
            {"code": "user:manage", "name": "管理用户", "module": "system"},
            {"code": "system:config", "name": "系统配置", "module": "system"},
        ]

        for perm in permissions_data:
            existing = db.query(Permission).filter(Permission.code == perm["code"]).first()
            if not existing:
                db.add(Permission(**perm))
        db.commit()
        print(f"[OK] {len(permissions_data)} 条权限记录已初始化")

        # 插入角色权限关联 (如果不存在)
        all_codes = [p["code"] for p in permissions_data]
        role_perms_map = {
            "super_admin": all_codes,  # 超级管理员: 所有权限
            "admin": [c for c in all_codes if not c.startswith(("system:", "user:", "log:"))],
            "teacher": ["student:view", "score:view", "score:create", "score:update",
                       "class:view", "course:view", "dashboard:view"],
            "student": ["student:view", "score:view", "class:view", "course:view",
                       "dashboard:view", "employment:view"],
        }

        for role, codes in role_perms_map.items():
            for code in codes:
                existing = db.query(RolePermission).filter(
                    RolePermission.role == role,
                    RolePermission.permission_code == code,
                ).first()
                if not existing:
                    db.add(RolePermission(role=role, permission_code=code))
        db.commit()
        print("[OK] 角色权限关联数据已初始化")

        # 插入默认超级管理员（如不存在）
        '''
        系统预置账号说明：
        ==========================================
        角色          用户名        密码
        ------------------------------------------
        超级管理员     super_admin    admin123
        普通管理员     admin1        123456
        教师           teacher1      123456
        学生           student1      123456
        ==========================================
        '''
        default_users = [
            {"username": "super_admin", "password": hash_password("admin123"),
             "role": "super_admin", "real_name": "系统管理员", "status": 1},
        ]
        for user_data in default_users:
            existing = db.query(User).filter(User.username == user_data["username"]).first()
            if not existing:
                db.add(User(**user_data))
        db.commit()
        print("[OK] 默认用户已初始化")

    finally:
        db.close()

    print("数据库初始化完成!")
    print("=" * 50)


if __name__ == "__main__":
    init_database()
