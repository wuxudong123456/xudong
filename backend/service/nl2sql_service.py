"""
NL2SQL 服务
将自然语言问题转换为SQL查询，带安全校验
安全约束: 仅允许SELECT, 禁止DROP/DELETE/UPDATE/INSERT/ALTER/TRUNCATE等
"""
import re
import logging
from typing import Dict, List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.utils.deepseek_util import chat_completion

logger = logging.getLogger(__name__)

# 数据库表结构（供DeepSeek生成SQL时参考）
DB_SCHEMA = """
数据库表结构:

1. teacher (teacher_id, teacher_name, gender, phone, identity, is_deleted, create_time, update_time)
2. class_info (class_id, class_name, start_time, close_time, head_teacher_id, lecturer_id, is_deleted, create_time, update_time)
3. student (id, student_no, class_id, student_name, gender, age, native_place, graduate_school, major, education, admission_time, graduate_time, advisor_id, job_open_time, is_deleted, create_time, update_time)
4. score (id, student_no, exam_order, score, is_deleted, create_time, update_time)
   -- 注: score通过student_no关联student表获取姓名和班级
5. employment (employment_id, student_no, student_name, class_id, offer_send_time, company_name, offer_job, final_choice, salary, is_deleted, create_time, update_time)
6. course_info (course_id, course_name, course_code, description, teacher_id, class_id, total_hours, is_deleted, create_time, update_time)
7. users (id, username, password, role, real_name, email, phone, avatar, status, last_login_time, is_deleted, create_time, update_time)

重要: 所有查询必须添加 `AND is_deleted = 0` 条件以过滤已删除数据。
表名使用反引号包裹(如`score`)以避免与SQL关键字冲突。
"""

# 禁止的SQL关键词
FORBIDDEN_KEYWORDS = [
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE",
    "CREATE", "REPLACE", "GRANT", "REVOKE", "EXEC", "EXECUTE",
    "INTO", "LOAD", "RENAME", "SHUTDOWN",
]

# 允许的表名白名单
ALLOWED_TABLES = ["teacher", "class_info", "student", "score", "employment",
                  "course_info", "users", "permissions", "role_permissions"]


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    SQL安全校验
    :param sql: 生成的SQL语句
    :return: (is_safe, error_message)
    """
    if not sql or not sql.strip():
        return False, "SQL语句为空"

    sql_upper = sql.upper().strip()

    # 1. 必须以SELECT开头
    if not sql_upper.startswith("SELECT"):
        return False, "仅允许SELECT查询语句"

    # 2. 检查禁止关键词
    for keyword in FORBIDDEN_KEYWORDS:
        # 使用词边界匹配（避免误判字段名中包含的关键词）
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, sql_upper):
            return False, f"SQL包含禁止操作: {keyword}"

    # 3. 检查表名白名单
    # 提取FROM和JOIN后的表名
    table_pattern = re.findall(
        r'(?:FROM|JOIN)\s+`?(\w+(?:-\w+)?)`?',
        sql, re.IGNORECASE
    )
    for table in table_pattern:
        if table.lower() not in [t.lower() for t in ALLOWED_TABLES]:
            return False, f"不允许访问的表: {table}"

    # 4. 长度限制
    if len(sql) > 2000:
        return False, "SQL语句过长"

    return True, ""


async def generate_sql(question: str) -> str:
    """
    使用DeepSeek将自然语言问题转换为SQL
    :param question: 用户自然语言问题，如"成绩最高的学生是谁"
    :return: SQL查询语句
    """
    prompt = f"""你是一个SQL专家。请根据以下数据库表结构，将用户的问题转换为MySQL查询语句。

{DB_SCHEMA}

要求：
1. 只生成SELECT语句，不要任何其他操作
2. 所有查询必须包含 `AND is_deleted = 0` 条件
3. 只返回SQL语句本身，不要任何解释或Markdown代码块标记
4. 如果问题无法转换为SQL，返回: --UNSUPPORTED

用户问题: {question}"""

    try:
        response = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500,
        )

        # 清理响应：去除可能的Markdown代码块标记
        sql = response.strip()
        sql = re.sub(r'^```sql\s*', '', sql)
        sql = re.sub(r'^```\s*', '', sql)
        sql = re.sub(r'\s*```$', '', sql)
        sql = sql.strip()

        if sql.startswith("--UNSUPPORTED"):
            return ""

        return sql
    except Exception as e:
        logger.error(f"SQL生成失败: {e}")
        return ""


def execute_nl2sql(db: Session, sql: str) -> Dict:
    """
    安全执行NL2SQL查询
    :param db: 数据库会话（使用只读连接更安全）
    :param sql: 经校验的SQL语句
    :return: {columns, rows, row_count}
    """
    try:
        result = db.execute(text(sql))
        columns = list(result.keys()) if result.returns_rows else []
        rows = [dict(zip(columns, row)) for row in result.fetchall()] if columns else []
        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
        }
    except Exception as e:
        logger.error(f"SQL执行失败: {e}")
        return {"columns": [], "rows": [], "row_count": 0, "error": str(e)}


async def nl2sql_query(db: Session, question: str) -> Dict:
    """
    NL2SQL完整流程: 自然语言 → SQL → 安全校验 → 执行 → 结果
    :param db: 数据库会话
    :param question: 用户自然语言问题
    :return: {question, sql, is_safe, result, error}
    """
    # Step 1: 生成SQL
    sql = await generate_sql(question)
    if not sql:
        return {
            "question": question,
            "sql": "",
            "is_safe": False,
            "result": None,
            "error": "无法将问题转换为SQL查询，请尝试更具体的问题。",
        }

    # Step 2: 安全校验
    is_safe, error_msg = validate_sql(sql)
    if not is_safe:
        return {
            "question": question,
            "sql": sql,
            "is_safe": False,
            "result": None,
            "error": f"SQL安全校验不通过: {error_msg}",
        }

    # Step 3: 执行查询
    result = execute_nl2sql(db, sql)

    return {
        "question": question,
        "sql": sql,
        "is_safe": True,
        "result": result,
        "error": result.get("error"),
    }
