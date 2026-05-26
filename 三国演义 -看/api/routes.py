"""API 路由：/api/retrieve 文件检索 + /api/qa 智能问答"""
from fastapi import APIRouter, HTTPException
from openai import OpenAI

from api.schemas import (
    RetrieveRequest, RetrieveResponse, RetrieveResult,
    QARequest, QAResponse, SourceItem,
)
from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
    DEFAULT_TOP_K,
)
from ingestion.milvus_store import Store

router = APIRouter(prefix="/api")

# 懒加载 Store（在 startup 中初始化）
store: Store | None = None


def get_store() -> Store:
    if store is None:
        raise HTTPException(500, "服务未初始化，请稍后再试")
    return store


def init_store(s: Store) -> None:
    global store
    store = s


QA_SYSTEM_PROMPT = """你是诸葛亮（字孔明），三国时期蜀汉丞相，先主刘备三顾茅庐请出的军师。你精通兵法谋略、天文地理，对《三国演义》中人物、事件、计谋了如指掌。

你正与主公（用户）对话。请以孔明的身份，根据以下参考资料解答主公的疑惑。

言语需：
- 半文半白，谦逊有礼，自称"孔明"或"亮"
- 若资料足以作答，引经据典，条理分明
- 若资料不足，如实相告，不可妄言编造
- 在回答末尾注明参考章回

参考资料：
{context}

主公所问：{question}

孔明答曰："""


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve(req: RetrieveRequest):
    s = get_store()
    results = s.search_file_chunks(req.query, req.top_k)

    items = [
        RetrieveResult(
            id=r["id"],
            chapter_num=r["chapter_num"],
            title=r["title"],
            chunk_index=r["chunk_index"],
            content=r["content"],
            score=round(r["score"], 4),
        )
        for r in results
    ]
    return RetrieveResponse(results=items, total=len(items))


@router.post("/qa", response_model=QAResponse)
def qa(req: QARequest):
    s = get_store()
    top_k = req.top_k or DEFAULT_TOP_K

    # 混合检索两张表
    search_results = s.hybrid_search(req.question, top_k)

    if not search_results:
        return QAResponse(
            answer="抱歉，未找到与您问题相关的《三国演义》内容。",
            sources=[],
        )

    # 构建上下文
    context_parts = []
    for i, r in enumerate(search_results):
        if r["type"] == "file_chunk":
            context_parts.append(
                f"[{i + 1}] 第{r['chapter_num']}回: {r['content'][:500]}"
            )
        elif r["type"] == "qa_pair":
            context_parts.append(
                f"[{i + 1}] 问答对 - Q: {r['question']}\nA: {r['answer'][:500]}"
            )

    context = "\n\n".join(context_parts)

    # 调用 DeepSeek
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    prompt = QA_SYSTEM_PROMPT.format(context=context, question=req.question)

    response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000,
    )
    answer = response.choices[0].message.content.strip()

    # 构建来源
    sources = []
    for r in search_results:
        src = SourceItem(
            type=r["type"],
            score=round(r["score"], 4),
        )
        if r["type"] == "file_chunk":
            src.chapter_num = r["chapter_num"]
            src.title = r["title"]
            src.content = r["content"][:300]
        elif r["type"] == "qa_pair":
            src.question = r["question"]
            src.answer = r["answer"][:300]
            src.chapter_num = r.get("source_chapter")
        sources.append(src)

    return QAResponse(answer=answer, sources=sources)
