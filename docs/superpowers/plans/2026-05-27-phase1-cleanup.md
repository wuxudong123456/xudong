# Phase 1: 基础清理与代码优化 实施计划

> **Goal:** 消除技术债务，建立统一的日志和配置基础
> **Architecture:** 统一日志系统 + DAO基类抽象 + 配置修正
> **Tech Stack:** Python logging, SQLAlchemy

---

## 文件变更总览

| 操作 | 文件 | 说明 |
|------|------|------|
| 新建 | `backend/utils/logger.py` | 统一日志配置 |
| 修改 | `backend/dao/base_dao.py` | 实现泛型DAO基类 |
| 修改 | `backend/dao/student_dao.py` | 继承BaseDAO |
| 修改 | `backend/dao/user_dao.py` | 继承BaseDAO |
| 修改 | `backend/config.py` | 增加日志配置 |
| 修改 | `backend/main.py` | 日志初始化 |
| 修改 | `backend/utils/embedding_util.py` | 修正注释 |
| 修改 | `backend/utils/milvus_util.py` | print→logging |
| 修改 | `backend/utils/text_chunker.py` | print→logging |
| 修改 | `backend/utils/deepseek_util.py` | print→logging |
| 修改 | `scripts/ingest_novel.py` | print→logging |
| 修改 | `scripts/init_milvus.py` | print→logging |
| 修改 | `scripts/init_db.py` | print→logging |

---

## Task 1: 统一日志配置

**Files:**
- 新建: `backend/utils/logger.py`
- 修改: `backend/config.py`

**Step 1: 创建日志配置模块**

```python
# backend/utils/logger.py
"""
统一日志配置模块
提供分级日志、按天轮转、多处理器支持
"""
import logging
import logging.handlers
import os
from pathlib import Path

# 日志目录
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志格式
DETAIL_FORMAT = "%(asctime)s [%(levelname)s] [%(name)s] %(filename)s:%(lineno)d - %(message)s"
SIMPLE_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"


def setup_logging(level=logging.INFO):
    """
    配置全局日志系统
    - 控制台输出: INFO级别以上
    - 应用日志文件: INFO级别以上，按天轮转
    - 错误日志文件: ERROR级别以上，按天轮转
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 清除已有处理器（避免重复）
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 控制台处理器
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(SIMPLE_FORMAT))
    root_logger.addHandler(console)

    # 应用日志文件 (按天轮转，保留7天)
    app_handler = logging.handlers.TimedRotatingFileHandler(
        filename=LOG_DIR / "app.log",
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(logging.Formatter(DETAIL_FORMAT))
    root_logger.addHandler(app_handler)

    # 错误日志文件
    error_handler = logging.handlers.TimedRotatingFileHandler(
        filename=LOG_DIR / "error.log",
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(DETAIL_FORMAT))
    root_logger.addHandler(error_handler)

    # AI调用专用日志
    ai_handler = logging.handlers.TimedRotatingFileHandler(
        filename=LOG_DIR / "ai.log",
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    ai_handler.setLevel(logging.INFO)
    ai_handler.setFormatter(logging.Formatter(DETAIL_FORMAT))
    ai_logger = logging.getLogger("ai")
    ai_logger.addHandler(ai_handler)
    ai_logger.propagate = False  # 避免重复输出到根日志

    logging.info("日志系统初始化完成")


def get_logger(name: str) -> logging.Logger:
    """获取命名日志器"""
    return logging.getLogger(name)
```

**Step 2: 在config.py增加日志配置**

在 `Settings` 类中增加:
```python
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", alias="LOG_LEVEL")
    LOG_DIR: str = Field(default="./logs", alias="LOG_DIR")
```

**Step 3: 在main.py初始化日志**

在 `lifespan` 启动时调用:
```python
from backend.utils.logger import setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化日志
    setup_logging()
    # ... 其余代码
```

---

## Task 2: 实现DAO泛型基类

**Files:**
- 修改: `backend/dao/base_dao.py`
- 修改: `backend/dao/student_dao.py`
- 修改: `backend/dao/user_dao.py`

**Step 1: 实现BaseDAO**

```python
# backend/dao/base_dao.py
"""
泛型DAO基类
提供通用的CRUD操作，支持软删除
"""
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

T = TypeVar("T")


class BaseDAO(Generic[T]):
    """
    泛型数据访问对象基类
    子类需指定: model_class
    """
    model_class: Type[T] = None

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, obj_id: int) -> Optional[T]:
        """根据ID查询，自动过滤已删除"""
        query = self.db.query(self.model_class).filter(
            self.model_class.id == obj_id
        )
        # 如果有is_deleted字段，过滤软删除
        if hasattr(self.model_class, "is_deleted"):
            query = query.filter(self.model_class.is_deleted == 0)
        return query.first()

    def get_page(
        self, page: int = 1, size: int = 20, **filters
    ) -> tuple:
        """
        分页查询
        :param filters: 额外过滤条件
        :return: (总记录数, 数据列表)
        """
        query = self.db.query(self.model_class)
        if hasattr(self.model_class, "is_deleted"):
            query = query.filter(self.model_class.is_deleted == 0)

        # 应用过滤条件
        for key, value in filters.items():
            if value is not None and hasattr(self.model_class, key):
                query = query.filter(getattr(self.model_class, key) == value)

        total = query.count()
        items = (
            query.order_by(self.model_class.id.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return total, items

    def create(self, data: Dict[str, Any]) -> T:
        """创建记录"""
        obj = self.model_class(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj_id: int, data: Dict[str, Any]) -> bool:
        """更新记录，过滤None值"""
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return False
        result = (
            self.db.query(self.model_class)
            .filter(self.model_class.id == obj_id)
            .update(update_data)
        )
        self.db.commit()
        return result > 0

    def soft_delete(self, obj_id: int) -> bool:
        """软删除"""
        if not hasattr(self.model_class, "is_deleted"):
            raise AttributeError(f"{self.model_class.__name__} 不支持软删除")
        result = (
            self.db.query(self.model_class)
            .filter(self.model_class.id == obj_id)
            .update({"is_deleted": 1})
        )
        self.db.commit()
        return result > 0

    def batch_soft_delete(self, ids: List[int]) -> int:
        """批量软删除"""
        if not hasattr(self.model_class, "is_deleted"):
            raise AttributeError(f"{self.model_class.__name__} 不支持软删除")
        result = (
            self.db.query(self.model_class)
            .filter(self.model_class.id.in_(ids))
            .update({"is_deleted": 1})
        )
        self.db.commit()
        return result

    def count(self, **filters) -> int:
        """统计记录数"""
        query = self.db.query(func.count(self.model_class.id))
        if hasattr(self.model_class, "is_deleted"):
            query = query.filter(self.model_class.is_deleted == 0)
        for key, value in filters.items():
            if value is not None and hasattr(self.model_class, key):
                query = query.filter(getattr(self.model_class, key) == value)
        return query.scalar() or 0
```

**Step 2: StudentDAO继承BaseDAO**

```python
# backend/dao/student_dao.py
from backend.dao.base_dao import BaseDAO
from backend.entity.student import Student

class StudentDAO(BaseDAO[Student]):
    model_class = Student

    def __init__(self, db: Session):
        super().__init__(db)
        # 保留自定义方法...
```

**Step 3: UserDAO继承BaseDAO**

类似改造...

---

## Task 3: 全局替换print为logging

**需要扫描的文件**:
- `backend/utils/milvus_util.py`
- `backend/utils/text_chunker.py`
- `backend/utils/deepseek_util.py`
- `scripts/ingest_novel.py`
- `scripts/init_milvus.py`
- `scripts/init_db.py`

**替换模式**:
```python
# 之前
print(f"[Milvus] 已连接到 {host}:{port}")

# 之后
import logging
logger = logging.getLogger(__name__)
logger.info("Milvus已连接到 %s:%s", host, port)
```

---

## Task 4: 配置修正

**Step 1: 修正embedding_util.py注释**

```python
# 之前（错误）
"""...512维..."""  # 但注释写1536维

# 之后
"""
Embedding向量化工具
使用本地BAAI/bge-small-zh-v1.5模型，512维
"""
VECTOR_DIM = 512  # bge-small-zh-v1.5输出维度
```

**Step 2: 标记未使用配置**

在 `config.py` 中:
```python
# 注意: 此配置当前未使用，实际使用NOVEL_COLLECTIONS字典
MILVUS_COLLECTION_NAME: str = Field(default="journey_to_the_west", alias="MILVUS_COLLECTION_NAME")
```

---

## 验证清单

- [ ] `backend/logs/` 目录自动创建
- [ ] `app.log` 记录INFO级别日志
- [ ] `error.log` 记录ERROR级别日志
- [ ] `ai.log` 记录AI调用
- [ ] StudentDAO能正常CRUD
- [ ] UserDAO能正常CRUD
- [ ] 所有模块无print()残留
- [ ] 应用正常启动无报错
