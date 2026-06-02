"""操作日志业务逻辑层 + 接口控制层"""
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.dependencies import get_db, get_current_user, require_role
from backend.entity.user import User
from backend.entity.operation_log import OperationLog

router = APIRouter()


class LogService:
    """操作日志服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_logs(self, page: int, size: int, module: str = None, action: str = None,
                  user_id: int = None, start_time: str = None, end_time: str = None) -> Dict[str, Any]:
        query = self.db.query(OperationLog)
        if module:
            query = query.filter(OperationLog.module == module)
        if action:
            query = query.filter(OperationLog.action == action)
        if user_id:
            query = query.filter(OperationLog.user_id == user_id)
        if start_time:
            query = query.filter(OperationLog.create_time >= datetime.fromisoformat(start_time))
        if end_time:
            query = query.filter(OperationLog.create_time <= datetime.fromisoformat(end_time))

        total = query.count()
        rows = query.order_by(OperationLog.id.desc()).offset((page - 1) * size).limit(size).all()
        items = [{
            "id": r.id, "user_id": r.user_id, "username": r.username,
            "module": r.module, "action": r.action, "target_type": r.target_type,
            "target_id": r.target_id, "detail": r.detail,
            "ip_address": r.ip_address,
            "create_time": r.create_time.isoformat() if r.create_time else None,
        } for r in rows]
        return {"items": items, "total": total, "page": page, "size": size,
                "pages": (total + size - 1) // size if size > 0 else 0}

    @staticmethod
    def record_log(db: Session, user_id: int, username: str, module: str, action: str,
                   target_type: str = None, target_id: str = None, detail: str = None,
                   ip_address: str = None, user_agent: str = None):
        """记录操作日志（静态方法，供各Service调用）"""
        log = OperationLog(
            user_id=user_id, username=username, module=module, action=action,
            target_type=target_type, target_id=target_id, detail=detail,
            ip_address=ip_address, user_agent=user_agent,
        )
        db.add(log)
        db.commit()


@router.get("/", summary="分页查询操作日志")
def list_logs(page: int = Query(1), size: int = Query(20, ge=1, le=100),
              module: Optional[str] = Query(None), action: Optional[str] = Query(None),
              user_id: Optional[int] = Query(None),
              start_time: Optional[str] = Query(None), end_time: Optional[str] = Query(None),
              db: Session = Depends(get_db),
              current_user: User = Depends(require_role("super_admin", "admin"))):
    service = LogService(db)
    return {"code": 200, "message": "查询成功",
            "data": service.list_logs(page, size, module, action, user_id, start_time, end_time)}
