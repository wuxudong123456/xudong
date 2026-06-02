"""成绩管理接口控制层"""
from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.dependencies import get_db, get_current_user, require_role
from backend.entity.user import User
from backend.service.score_service import ScoreService
from backend.schema.score_schema import ScoreCreate, ScoreUpdate, ScoreBatchImport

router = APIRouter()


@router.get("/", summary="分页查询成绩列表")
def list_scores(
    page: int = Query(1), size: int = Query(20, ge=1, le=100),
    student_no: Optional[str] = Query(None), class_id: Optional[int] = Query(None),
    exam_order: Optional[int] = Query(None),
    score_min: Optional[Decimal] = Query(None), score_max: Optional[Decimal] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分页查询成绩，支持按班级、考试序次、分数区间筛选"""
    service = ScoreService(db)
    result = service.list_scores(page, size, student_no, class_id, exam_order, score_min, score_max)
    return {"code": 200, "message": "查询成功", "data": result}


@router.post("/", summary="录入成绩")
def create_score(score: ScoreCreate, db: Session = Depends(get_db),
                 current_user: User = Depends(require_role("super_admin", "admin", "teacher"))):
    service = ScoreService(db)
    return {"code": 200, "message": "录入成功", "data": service.create_score(score.model_dump())}


@router.put("/{score_id}", summary="编辑成绩")
def update_score(score_id: int, score: ScoreUpdate, db: Session = Depends(get_db),
                 current_user: User = Depends(require_role("super_admin", "admin", "teacher"))):
    service = ScoreService(db)
    return {"code": 200, "message": "编辑成功",
            "data": service.update_score(score_id, score.model_dump(exclude_none=True))}


@router.delete("/{score_id}", summary="删除成绩")
def delete_score(score_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(require_role("super_admin", "admin"))):
    service = ScoreService(db)
    service.delete_score(score_id)
    return {"code": 200, "message": "删除成功", "data": None}


@router.post("/import", summary="批量导入成绩")
async def import_scores(file: UploadFile = File(...), db: Session = Depends(get_db),
                        current_user: User = Depends(require_role("super_admin", "admin", "teacher"))):
    if not file.filename.endswith('.xlsx'):
        return {"code": 400, "message": "仅支持.xlsx文件", "data": None}
    service = ScoreService(db)
    result = service.import_excel(file)
    return {"code": 200, "message": f"导入完成: 成功{result['success']}条, 失败{result['fail']}条", "data": result}


@router.get("/export", summary="导出成绩Excel")
def export_scores(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = ScoreService(db)
    excel_bytes = service.export_excel()
    return StreamingResponse(excel_bytes,
                             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=scores.xlsx"})


@router.get("/stats", summary="成绩统计")
def score_stats(exam_order: Optional[int] = Query(None), db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    service = ScoreService(db)
    return {"code": 200, "message": "查询成功", "data": service.get_stats(exam_order)}


@router.get("/rankings", summary="成绩排名")
def score_rankings(exam_order: Optional[int] = Query(None), top_n: int = Query(20),
                   db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = ScoreService(db)
    return {"code": 200, "message": "查询成功", "data": service.get_rankings(exam_order, top_n)}
