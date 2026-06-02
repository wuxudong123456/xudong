"""FastAPI 应用入口：挂载路由 + 静态文件 + 生命周期"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router, init_store
from ingestion.milvus_store import Store

import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时初始化 Milvus 连接"""
    print("正在连接 Milvus...")
    s = Store()
    init_store(s)

    from config import FILE_CHUNKS_COLLECTION, QA_PAIRS_COLLECTION
    if s.client.has_collection(FILE_CHUNKS_COLLECTION):
        s.client.load_collection(FILE_CHUNKS_COLLECTION)
        print(f"集合 {FILE_CHUNKS_COLLECTION} 已加载")
    else:
        print(f"警告: 集合 {FILE_CHUNKS_COLLECTION} 不存在")

    if s.client.has_collection(QA_PAIRS_COLLECTION):
        s.client.load_collection(QA_PAIRS_COLLECTION)
        print(f"集合 {QA_PAIRS_COLLECTION} 已加载")
    else:
        print(f"警告: 集合 {QA_PAIRS_COLLECTION} 不存在")

    yield
    print("服务关闭")


app = FastAPI(
    title="三国演义 RAG 问答系统",
    description="基于 RAG 的《三国演义》智能问答 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# 挂载静态文件目录（前端界面）
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8080, reload=True)
