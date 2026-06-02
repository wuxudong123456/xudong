"""
人物关系图谱API控制器
提供人物关系查询、图谱可视化数据
"""
from fastapi import APIRouter, Query
from typing import Optional
from backend.service.graph_service import GraphService
from backend.utils.logger import get_logger

router = APIRouter()
logger = get_logger("graph_controller")


@router.get("/person/{name}", summary="查询人物信息")
async def get_person_info(name: str):
    """获取人物详细信息和关系网络"""
    service = GraphService()
    if not service.is_ready():
        return {"code": 503, "message": "图谱服务未就绪", "data": None}

    result = service.get_person_relations(name)
    if result.get("error"):
        return {"code": 404, "message": result["error"], "data": None}

    return {"code": 200, "message": "success", "data": result}


@router.get("/path", summary="查询人物关系路径")
async def find_relation_path(
    from_name: str = Query(..., description="起始人物"),
    to_name: str = Query(..., description="目标人物"),
):
    """查找两个人物之间的关系路径"""
    service = GraphService()
    if not service.is_ready():
        return {"code": 503, "message": "图谱服务未就绪", "data": None}

    result = service.find_relation_path(from_name, to_name)
    return {"code": 200, "message": "success", "data": result}


@router.get("/book/{book_name}", summary="获取名著人物列表")
async def get_book_characters(book_name: str):
    """获取某本名著的所有人物"""
    service = GraphService()
    if not service.is_ready():
        return {"code": 503, "message": "图谱服务未就绪", "data": None}

    characters = service.get_book_characters(book_name)
    return {"code": 200, "message": "success", "data": characters}


@router.get("/visualization", summary="获取图谱可视化数据")
async def get_graph_visualization(
    book: Optional[str] = Query(None, description="筛选名著，如 novel_sanguo"),
    center: Optional[str] = Query(None, description="中心人物"),
):
    """获取ECharts可用的图谱数据"""
    service = GraphService()
    if not service.is_ready():
        return {"code": 503, "message": "图谱服务未就绪", "data": None}

    data = service.get_graph_visualization_data(book=book, center_name=center)
    return {"code": 200, "message": "success", "data": data}


@router.get("/search", summary="搜索人物")
async def search_person(keyword: str = Query(..., description="搜索关键词")):
    """模糊搜索人物"""
    service = GraphService()
    if not service.is_ready():
        return {"code": 503, "message": "图谱服务未就绪", "data": None}

    results = service.search_person(keyword)
    return {"code": 200, "message": "success", "data": results}
