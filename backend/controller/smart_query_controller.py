"""
智能问数控制器
自然语言 → SQL → 执行 → LLM自然语言回答
SQL 失败或 0 结果时 → 记忆系统回退
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from backend.dependencies import get_db, get_current_user
from backend.entity.user import User
from backend.service.nl2sql_service import nl2sql_query
from backend.utils.deepseek_util import chat_completion

router = APIRouter()


class SmartQueryRequest(BaseModel):
    question: str = Field(..., description="自然语言问题，如：成绩最高的学生是谁")


async def _memory_fallback(db: Session, user_id: int, question: str) -> str:
    """SQL 查不到时，从记忆系统找答案"""
    from backend.service.memory_service import MemoryService
    memory = MemoryService(db)
    recent = memory.get_query_history(user_id)[:5]
    if not recent:
        return ""
    q_list = "\n".join([f"- {r['question']}" for r in recent])
    prompt = f"""用户问："{question}"
该用户最近的查询记录：
{q_list}

请直接用猪八戒口吻（自称"俺老猪"）回答用户。比如用户问"上一个问题是什么"，
告诉他最近问了什么。不要解释你在查记录。"""
    answer = await chat_completion(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5, max_tokens=200,
    )
    return answer.strip()


@router.post("/", summary="智能问数")
async def smart_query(
    req: SmartQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    nl2sql_result = await nl2sql_query(db, req.question) or {}
    result = nl2sql_result.get("result") or {}
    rows = result.get("rows", [])
    columns = result.get("columns", [])
    row_count = result.get("row_count", 0)
    sql = nl2sql_result.get("sql", "")
    error = nl2sql_result.get("error")

    # SQL 查到了数据 → LLM 生成自然语言回答
    if row_count > 0:
        data_sample = rows[:10]
        data_text = "\n".join(
            [", ".join(f"{k}: {v}" for k, v in row.items()) for row in data_sample]
        )
        prompt = f"""你是猪八戒，用口语句子回答用户问题。

用户问题：{req.question}
查询结果（共{row_count}条，显示前{min(row_count, 10)}条）：
{data_text}

用猪八戒口吻（自称"俺老猪"）直接回答。把数据融入回答，不要提SQL技术细节。"""
        answer = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7, max_tokens=300,
        )
        answer = answer.strip()
        if row_count > 10:
            answer += f"（共查到{row_count}条，只显示了前10条）"
    else:
        # SQL 失败或 0 结果 → 记忆回退
        answer = await _memory_fallback(db, current_user.id, req.question)
        if not answer:
            err_msg = error or "没找到相关数据"
            answer = f"哼哼～{err_msg}。要不换个问题试试？"

    # 自动存档
    from backend.service.memory_service import MemoryService
    MemoryService(db).save_query(
        current_user.id, f"{current_user.id}_query",
        req.question, answer, sql=sql, row_count=row_count,
    )

    return {
        "code": 200, "message": "success",
        "data": {
            "question": req.question, "sql": sql,
            "data": rows[:50], "columns": columns,
            "answer": answer, "row_count": row_count,
        },
    }
