"""仪表盘接口控制层"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.dependencies import get_db, get_current_user
from backend.entity.user import User
from backend.service.dashboard_service import DashboardService

router = APIRouter()


@router.get("/overview", summary="仪表盘概览数据")
def get_overview(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """返回: 学生总数、班级数、教师数、平均分、就业率"""
    service = DashboardService(db)
    return {"code": 200, "message": "查询成功", "data": service.get_overview()}


@router.get("/class-distribution", summary="班级学生分布")
def class_distribution(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """各班级学生人数分布(饼图)"""
    service = DashboardService(db)
    return {"code": 200, "message": "查询成功", "data": service.get_class_distribution()}


@router.get("/score-trend", summary="成绩趋势")
def score_trend(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """各次考试平均分趋势(折线图)"""
    service = DashboardService(db)
    return {"code": 200, "message": "查询成功", "data": service.get_score_trend()}


@router.get("/employment-rate", summary="就业情况")
def employment_rate(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """各班就业人数和平均薪资(柱状图)"""
    service = DashboardService(db)
    return {"code": 200, "message": "查询成功", "data": service.get_employment_by_class()}


@router.get("/score-distribution", summary="成绩分布")
def score_distribution(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """成绩分数段分布"""
    service = DashboardService(db)
    return {"code": 200, "message": "查询成功", "data": service.get_score_distribution()}
