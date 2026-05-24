"""
数据访问层基类模块
提供泛型CRUD操作基类，所有实体DAO继承此类
"""
from typing import TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from backend.entity.base import Base

T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    """
    泛型DAO基类，封装通用CRUD操作
    使用方式: class StudentDAO(BaseDAO[Student]): ...
    """

    def __init__(self, model: type, db: Session):
        """
        初始化DAO
        :param model: SQLAlchemy实体类
        :param db: 数据库会话
        """
        self.model = model
        self.db = db

    def get_by_id(self, id_value: int) -> Optional[T]:
        """根据主键ID查询单条记录，自动过滤软删除"""
        return (
            self.db.query(self.model)
            .filter(
                self.model.__dict__.get("is_deleted") == 0,
                self._get_pk_column() == id_value,
            )
            .first()
        )

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """
        根据过滤条件查询所有记录
        :param filters: 字段名->值的过滤字典，如 {"class_id": 1}
        """
        query = self.db.query(self.model)
        if hasattr(self.model, "is_deleted"):
            query = query.filter(self.model.is_deleted == 0)
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.filter(getattr(self.model, field) == value)
        return query.all()

    def get_page(
        self,
        page: int = 1,
        size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        like_filters: Optional[Dict[str, str]] = None,
        order_by: Optional[Any] = None,
    ) -> tuple[int, List[T]]:
        """
        分页查询
        :param page: 页码(从1开始)
        :param size: 每页条数
        :param filters: 精确匹配条件 {"class_id": 1}
        :param like_filters: 模糊匹配条件 {"student_name": "张三"}
        :param order_by: 排序列
        :return: (总条数, 当前页记录列表)
        """
        query = self.db.query(self.model)
        # 自动过滤软删除
        if hasattr(self.model, "is_deleted"):
            query = query.filter(self.model.is_deleted == 0)
        # 精确匹配条件
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.filter(getattr(self.model, field) == value)
        # 模糊匹配条件 (LIKE)
        if like_filters:
            for field, value in like_filters.items():
                if hasattr(self.model, field) and value:
                    query = query.filter(getattr(self.model, field).like(f"%{value}%"))
        # 排序
        if order_by is not None:
            query = query.order_by(order_by)
        # 计算总数
        total = query.count()
        # 分页
        items = query.offset((page - 1) * size).limit(size).all()
        return total, items

    def create(self, data: dict) -> T:
        """
        创建新记录
        :param data: 实体字段字典
        :return: 创建的实体对象
        """
        instance = self.model(**data)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def batch_create(self, data_list: List[dict]) -> List[T]:
        """批量创建记录"""
        instances = [self.model(**data) for data in data_list]
        self.db.add_all(instances)
        self.db.commit()
        return instances

    def update(self, id_value: int, data: dict) -> Optional[T]:
        """
        更新记录
        :param id_value: 主键ID
        :param data: 需要更新的字段字典
        :return: 更新后的实体对象
        """
        instance = self.get_by_id(id_value)
        if not instance:
            return None
        for field, value in data.items():
            if hasattr(instance, field) and value is not None:
                setattr(instance, field, value)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def soft_delete(self, id_value: int) -> bool:
        """
        软删除: 将 is_deleted 标记为 1
        :param id_value: 主键ID
        :return: 是否成功
        """
        instance = self.get_by_id(id_value)
        if not instance:
            return False
        instance.is_deleted = 1
        self.db.commit()
        return True

    def hard_delete(self, id_value: int) -> bool:
        """物理删除记录（慎用）"""
        instance = self.get_by_id(id_value)
        if not instance:
            return False
        self.db.delete(instance)
        self.db.commit()
        return True

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """统计记录数量"""
        query = self.db.query(func.count(self._get_pk_column()))
        if hasattr(self.model, "is_deleted"):
            query = query.filter(self.model.is_deleted == 0)
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.filter(getattr(self.model, field) == value)
        return query.scalar() or 0

    def exists(self, field: str, value: Any, exclude_id: Optional[int] = None) -> bool:
        """
        检查字段值是否已存在(去重校验)
        :param field: 字段名
        :param value: 字段值
        :param exclude_id: 排除的记录ID(编辑时排除自身)
        """
        query = self.db.query(self.model).filter(
            getattr(self.model, field) == value
        )
        if hasattr(self.model, "is_deleted"):
            query = query.filter(self.model.is_deleted == 0)
        if exclude_id:
            pk_col = self._get_pk_column()
            query = query.filter(pk_col != exclude_id)
        return query.first() is not None

    def _get_pk_column(self):
        """获取主键列"""
        from sqlalchemy import inspect
        for col in inspect(self.model).primary_key:
            return col
        return self.model.id  # fallback
