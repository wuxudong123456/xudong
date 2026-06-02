"""
生成答辩PPT：学生管理系统 + 猪八戒多智能体 AI 平台
深色古典主题，14 页
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# 主题色
DARK_BG = RGBColor(0x1B, 0x2A, 0x4A)
GOLD = RGBColor(0xC9, 0xA9, 0x6E)
RICE = RGBColor(0xF5, 0xE6, 0xC8)
VERMILION = RGBColor(0xC4, 0x3B, 0x3B)
BAMBOO = RGBColor(0x5D, 0x8A, 0x5D)
INDIGO_LIGHT = RGBColor(0x2C, 0x3E, 0x6B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DIM = RGBColor(0x90, 0x93, 0x99)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

def add_bg(slide):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = DARK_BG

def add_title_bar(slide, title_text, subtitle_text=""):
    """顶部金色标题栏"""
    # 标题
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.7))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(30)
    p.font.bold = True
    p.font.color.rgb = GOLD
    # 金色底线
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.15), Inches(11.7), Pt(3))
    line.fill.solid()
    line.fill.fore_color.rgb = GOLD
    line.line.fill.background()
    if subtitle_text:
        txBox2 = slide.shapes.add_textbox(Inches(0.8), Inches(1.25), Inches(11.7), Inches(0.4))
        tf2 = txBox2.text_frame
        p2 = tf2.paragraphs[0]
        p2.text = subtitle_text
        p2.font.size = Pt(14)
        p2.font.color.rgb = DIM

def add_body(slide, lines, top=1.8, left=0.8, width=7.5, font_size=16):
    """正文列表"""
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(4.5))
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = line
        p.font.size = Pt(font_size)
        p.font.color.rgb = RICE
        p.space_after = Pt(8)
        if line.startswith("●"):
            p.font.bold = True
            p.font.color.rgb = GOLD
        elif line.startswith("▸"):
            p.font.color.rgb = RICE
            p.level = 1

def add_highlight_box(slide, title, content, top=5.5):
    """底部技术亮点色块"""
    # 背景色块
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top), Inches(11.7), Inches(1.6))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0x22, 0x35, 0x50)
    shape.line.fill.background()
    # 标签
    txBox = slide.shapes.add_textbox(Inches(1.0), Inches(top + 0.1), Inches(11.3), Inches(0.3))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "★ 技术亮点"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = VERMILION
    # 内容
    txBox2 = slide.shapes.add_textbox(Inches(1.0), Inches(top + 0.45), Inches(11.3), Inches(1.0))
    tf2 = txBox2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = content
    p2.font.size = Pt(13)
    p2.font.color.rgb = RICE

def add_principle_box(slide, title, content, top=5.5):
    """底部实现原理色块（绿色系）"""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top), Inches(11.7), Inches(1.6))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0x1A, 0x2E, 0x1A)
    shape.line.fill.background()
    txBox = slide.shapes.add_textbox(Inches(1.0), Inches(top + 0.1), Inches(11.3), Inches(0.3))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = f"⚙ 实现原理：{title}"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = BAMBOO
    txBox2 = slide.shapes.add_textbox(Inches(1.0), Inches(top + 0.45), Inches(11.3), Inches(1.0))
    tf2 = txBox2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = content
    p2.font.size = Pt(13)
    p2.font.color.rgb = RICE

def add_page_number(slide, num):
    txBox = slide.shapes.add_textbox(Inches(12.0), Inches(7.0), Inches(1.0), Inches(0.4))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = f"{num}/14"
    p.font.size = Pt(10)
    p.font.color.rgb = DIM
    p.alignment = PP_ALIGN.RIGHT

# ============================================================
# Slide 1: 封面
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
# 装饰线
line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.5), Inches(2.2), Inches(4.3), Pt(4))
line.fill.solid(); line.fill.fore_color.rgb = GOLD; line.line.fill.background()
# 标题
txBox = slide.shapes.add_textbox(Inches(1.5), Inches(2.5), Inches(10.3), Inches(1.5))
tf = txBox.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "学生管理系统 + 猪八戒多智能体 AI 平台"
p.font.size = Pt(42); p.font.bold = True; p.font.color.rgb = GOLD; p.alignment = PP_ALIGN.CENTER
p2 = tf.add_paragraph()
p2.text = "基于 FastAPI + Vue3 + DeepSeek 的教育管理智能系统"
p2.font.size = Pt(20); p2.font.color.rgb = RICE; p2.alignment = PP_ALIGN.CENTER; p2.space_before = Pt(8)
# 底部信息
txBox2 = slide.shapes.add_textbox(Inches(3), Inches(5.5), Inches(7.3), Inches(1.0))
tf2 = txBox2.text_frame
p3 = tf2.paragraphs[0]
p3.text = "8 个管理模块 · 4 个 AI 角色 · 9 种意图分类 · 6 个智能工具 · 3 层记忆系统"
p3.font.size = Pt(16); p3.font.color.rgb = DIM; p3.alignment = PP_ALIGN.CENTER
p4 = tf2.add_paragraph()
p4.text = "答辩演示 · 2026 年 6 月"
p4.font.size = Pt(14); p4.font.color.rgb = DIM; p4.alignment = PP_ALIGN.CENTER; p4.space_before = Pt(16)

# ============================================================
# Slide 2: 项目概述
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_title_bar(slide, "项目概述", "一句话定位 + 核心数字")
add_body(slide, [
    "● 定位",
    "  面向教育机构的学生数据管理平台，集成猪八戒四大名著角色多智能体 AI 对话系统",
    "",
    "● 核心数字",
    "▸ 管理模块：7 大 CRUD（学生/班级/成绩/就业/课程/日志/用户）+ 仪表盘 + 智能问数",
    "▸ AI 角色：猪八戒 · 鲁智深 · 林黛玉 · 诸葛亮（4 个四大名著人物可切换对话）",
    "▸ 意图分类：9 种意图（数据查询/知识问答/情绪疏导/社交帮助/天气/运势/灯谜/飞花令/闲聊）",
    "▸ 智能工具：NL2SQL · RAG 知识检索 · Neo4j 图谱 · 天气 · 运势 · 数学计算",
    "▸ 记忆系统：短期上下文 + 长期 MySQL/Milvus 双写 + 用户画像",
    "▸ 技术栈：FastAPI + Vue3 + ElementPlus + MySQL + Milvus + Neo4j + DeepSeek",
    "▸ 代码规模：后端 60+ 文件 · 前端 30+ 组件 · Python/Vue/SCSS 三语言",
])
add_page_number(slide, 2)

# ============================================================
# Slide 3: 技术架构全景图
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_title_bar(slide, "技术架构全景图", "三层架构 + 多智能体编排核心")
add_body(slide, [
    "● 前端层（Vue3 + Element Plus + ECharts）",
    "  ▸ 古典四大名著主题（朱红/黛蓝/宣纸黄/金色 CSS 变量系统）",
    "  ▸ 20+ 页面组件 · TabBar 标签页 · 语音输入输出 · 主动消息推送",
    "",
    "● 后端层（FastAPI + SQLAlchemy + DeepSeek）",
    "  ▸ Agent 编排器（OrchestratorAgent）—— 任务分解 → 并行调度 → 结果合并",
    "  ▸ 8 个专家 Agent（Data/Knowledge/Emotional/Social/Game/Persona/Weather/Fortune）",
    "  ▸ ReAct 推理循环 + Function Calling 工具调用 + 贝叶斯意图分类",
    "",
    "● 数据层",
    "  ▸ MySQL：业务数据（学生/成绩/班级/用户/记忆碎片/用户画像）",
    "  ▸ Milvus：四大名著向量库（512 维 BGE Embedding）+ 记忆向量检索",
    "  ▸ Neo4j：64 人物节点 + Event 事件节点 + CAUSES 因果边",
])
add_highlight_box(slide, "核心创新点", "多智能体编排层——Orchestrator 将 LLM 意图分类 → 贝叶斯快速路由 → TaskDecomposer 分解 → asyncio.gather 并行执行 → LLM 合并，形成完整的感知-决策-执行链路", top=6.0)
add_page_number(slide, 3)

# ============================================================
# Slide 4: 管理系统模块
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_title_bar(slide, "管理系统 7 大模块", "CRUD + 导入导出 + 智能问数 + 仪表盘")
add_body(slide, [
    "● 数据管理",
    "  ▸ 学生/班级/成绩/就业/课程 — 完整的增删改查 + 批量操作 + Excel 导入导出",
    "  ▸ 操作日志 — 记录所有管理员操作，支持按模块/时间筛选",
    "  ▸ 用户管理 — 基于 RBAC 权限模型（super_admin/admin/teacher/student）",
    "",
    "● 数据看板",
    "  ▸ ECharts 可视化：班级分布饼图 · 成绩趋势折线图 · 就业率柱状图 · 分数段分布",
    "",
    "● 智能问数（每个管理页面顶部）",
    "  ▸ 自然语言输入 → DeepSeek 生成 SQL → 安全校验（仅允许 SELECT + 表名白名单）",
    "  ▸ → 执行 → LLM 将结果转为口语回答 → 同时展示数据表格",
    "  ▸ 查询历史自动记录，支持点击复用",
])
add_principle_box(slide, "NL2SQL 智能问数",
    "用户自然语言（如\"各班级平均分排名\"）→ DeepSeek 根据预定义 DB Schema 生成 MySQL 查询 → validate_sql() 安全校验（仅允许 SELECT + 表名白名单 + 禁止关键词检测）→ SQLAlchemy text() 执行 → LLM 将行数据转为口语回答（猪八戒口吻）。SQL 失败时自动回退到查询历史记忆。")
add_page_number(slide, 4)

# ============================================================
# Slide 5: 多智能体协同
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_title_bar(slide, "多智能体协同架构", "8 Agent + Orchestrator + ReAct + Function Calling")
add_body(slide, [
    "● Agent 矩阵（8 个专家，继承 BaseAgent 抽象基类）",
    "  DataAgent / KnowledgeAgent / EmotionalAgent / SocialAgent",
    "  GameAgent / PersonaAgent / WeatherAgent / FortuneAgent",
    "  + ReactAgent（推理循环） + RecommendationAgent（学习推荐）",
    "",
    "● Orchestrator 编排流水线",
    "  ① TaskDecomposer 分析是否复合问题（LLM 判断 → 最多拆分 3 个子任务）",
    "  ② 复合 → asyncio.gather 并行执行 → LLM 合并回答（agent: MultiAgentSystem）",
    "  ③ 单一 → execute_single() 原路由表分发",
    "",
    "● AgentMessageBus（共享上下文）",
    "  线程安全 dict，agent 间通过 bus.set/get 交换信息",
])
add_principle_box(slide, "Orchestrator 编排器",
    "用户消息 → TaskDecomposer.decompose() 用 LLM 分析是单一问题还是复合问题 → 复合则拆分 [{intent, sub_message, order}] → asyncio.gather 并行调 execute_single() → 收集结果 → LLM merge：\"你是{角色}，以下是不同角度信息...整合成连贯回复\"")
add_page_number(slide, 5)

# ============================================================
# Slide 6: 四大名著角色对话
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_title_bar(slide, "四大名著角色对话", "4 角色下拉切换 + Identity Injection + 混合意图分类")
add_body(slide, [
    "● 角色系统",
    "  ▸ 猪八戒（西游记）自称\"俺老猪\" / 鲁智深（水浒传）自称\"洒家\"",
    "  ▸ 林黛玉（红楼梦）自称\"颦儿\" / 诸葛亮（三国演义）自称\"亮\"",
    "  ▸ 每个角色独立的 system_prompt + 绝对禁止串词",
    "",
    "● 核心技术",
    "  ▸ Identity Injection：将角色身份作为首条 user 消息注入（比 system prompt 更有效）",
    "  ▸ 前端下拉框选择 + 左侧会话列表（按角色分组）",
    "  ▸ 全部 4 角色共用 Agent 工具箱（天气/运势/数据查询/知识问答）",
    "",
    "● 意图分类：贝叶斯 + LLM 混合",
])
add_principle_box(slide, "贝叶斯 + LLM 混合分类",
    "MultinomialNB + TF-IDF(char_wb, 1-3 gram) 本地分类。训练数据：DB 历史消息 + 种子关键词。置信度 ≥ 0.85 直接用贝叶斯（<1ms 本地计算，零网络开销）；< 0.85 回退 DeepSeek LLM 分类。LLM 结果自动加入训练缓冲区，累计 20 条触发增量重训练。")
add_page_number(slide, 6)

# ============================================================
# Slide 7: 三层记忆系统
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_title_bar(slide, "三层记忆系统", "短期上下文 + 长期存储 + 用户画像")
add_body(slide, [
    "● 第一层：短期对话上下文",
    "  ▸ 前端维护最近 10 轮对话 → 随 API 请求发送 → LLM 作为对话历史参考",
    "  ▸ 会话管理：左侧会话列表（新建/切换/删除），每角色独立分组",
    "",
    "● 第二层：长期记忆（MySQL + Milvus 双写）",
    "  ▸ 对话结束后 fire-and-forget 异步提取 → LLM 识别 fact/preference/event/emotion",
    "  ▸ Jaccard 文本相似度去重（阈值 0.3）→ BGE Embedding 向量化（512 维）",
    "  ▸ 双写 MySQL memory_fragments + Milvus memory_vectors",
    "",
    "● 第三层：用户画像",
    "  ▸ user_profiles：交互计数 / 偏好话题 / 性格标签 / 最近情绪 / 主动搭话开关",
])
add_highlight_box(slide, "fire-and-forget 记忆提取",
    "每轮对话结束后 → MemoryExtractor.extract_memories(user_id, conversation) → asyncio.create_task 后台异步执行 → 独立 DB Session（不阻塞 HTTP 响应）→ LLM 提取关键信息 → 去重 → 向量化 → 双写 → 更新画像。用户完全无感知，响应时间不受影响。",
    top=5.8)
add_page_number(slide, 7)

# ============================================================
# Slide 8: RAG 检索增强生成
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_title_bar(slide, "RAG 检索增强生成", "四大名著向量库 + 自动/原文/图谱/融合四模式")
add_body(slide, [
    "● 数据管道",
    "  ▸ 四大名著全文（西游/三国/红楼/水浒）→ text_chunker 章回切分 → BGE Embedding",
    "  ▸ → Milvus 4 个独立 Collection（每书一库，保证语义隔离）",
    "  ▸ 每库字段：chunk_id / chapter_num / chapter_title / content / embedding(512维)",
    "",
    "● 检索模式（4 种）",
    "  ▸ 自动检索：关键词检测 → 自动路由（关系类→图谱 / 内容类→RAG）",
    "  ▸ 原文检索：问题→向量化→Milvus COSINE 搜索 Top-K→原文拼接→LLM 回答",
    "  ▸ 图谱查询：Neo4j Cypher 查人物关系网络 + LLM 解释",
    "  ▸ 融合查询：RAG + 图谱 asyncio.gather 并行 → LLM 综合回答",
])
add_principle_box(slide, "RAG 全流程",
    "用户问题 → BGE-small-zh-v1.5 向量化（512维）→ book_router 智能判断查哪本书 → search_specific_novels(Milvus COSINE, top_k=5, filter by collection) → 原文片段拼接 → system prompt 注入\"根据以下原文回答\" → DeepSeek 生成答案 + 注明出处（书名/章回/原文/相似度）。支持多集合跨书联合检索。")
add_page_number(slide, 8)

# ============================================================
# Slide 9: Neo4j 知识图谱
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_title_bar(slide, "Neo4j 知识图谱推理", "64 人物节点 + 关系网络 + 因果链 + 阵营分析")
add_body(slide, [
    "● 图数据模型",
    "  ▸ Person 节点：name / identity / book / aliases / faction / appears_in_chapter",
    "  ▸ Event 节点（新增）：name / chapter / description / event_type（major_event/scene/battle）",
    "  ▸ 关系边：RELATIONSHIP（人物关系）/ CAUSES（因果边，Event→Event）",
    "",
    "● 推理能力",
    "  ▸ 因果链：给定事件→Cypher 沿 CAUSES 边遍历 1-5 跳→LLM 将链转为故事叙述",
    "  ▸ 阵营分析：MATCH (p:Person {faction:'蜀'}) → 成员列表 + 身份统计",
    "  ▸ 事件时间线：MATCH (e:Event {book:'novel_xiyou'}) ORDER BY chapter → 大事年表",
    "  ▸ 深度问答：LLM 分析问题类型→自动选择因果/阵营/时间线/关系方法执行",
])
add_principle_box(slide, "GraphReasoningService",
    "deep_query(question) → LLM 解析问题类型 {\"type\":\"causal\"|\"faction\"|\"timeline\"|\"relation\",\"target\":\"...\"} → 路由到对应 Cypher 查询 → LLM 将查询结果转为自然语言解释。所有 Cypher 用 try/except 包裹，Neo4j 不可用时返回友好提示。")
add_page_number(slide, 9)

# ============================================================
# Slide 10: BKT 学习推荐
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_title_bar(slide, "BKT 学习推荐系统", "贝叶斯知识追踪 + 趋势诊断 + LLM 学习计划")
add_body(slide, [
    "● BKT 算法（简化版，不依赖 ML 库）",
    "  ▸ P_init = 0.5（初始掌握概率）",
    "  ▸ 每轮考试：score ≥ 60 → P = P + (1-P) × 0.2（学习增益）",
    "  ▸           score < 60 → P = P × 0.9（考虑失误率衰减）",
    "  ▸ P ≥ 0.8 → \"mastered\" / 0.4-0.8 → \"learning\" / < 0.4 → \"weak\"",
    "",
    "● 薄弱点诊断",
    "  ▸ 按 exam_order 排序 → 计算前后半段均分差 → 标记趋势（declining/stable/improving）",
    "  ▸ 逐次比较检测成绩下降点 → 生成 weak_points 列表",
    "",
    "● 学习计划生成（LLM）",
    "  ▸ 输入：学生姓名 + 历次成绩 + 趋势 + 薄弱点 → Prompt → 重点复习方向/时间建议/练习推荐",
])
add_highlight_box(slide, "P(known) 迭代公式",
    "P_new = P_old + (1-P_old) × 0.2（及格） 或 P_old × 0.9（不及格）。纯数值计算，无需 ML 库。仅需 ≥2 次考试成绩即可诊断。RecommendationAgent 自动提取学号（正则 S\\d{4,}），匹配\"学习计划/诊断/薄弱\"关键词后路由。",
    top=5.8)
add_page_number(slide, 10)

# ============================================================
# Slide 11: ReAct 推理循环
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_title_bar(slide, "ReAct 推理循环", "Reasoning + Acting：LLM 自主工具调用推理")
add_body(slide, [
    "● ReAct 循环流程（最多 5 轮）",
    "  ① LLM 接收问题 → 输出 JSON: {thought: \"分析\", action: {tool: \"nl2sql\", input: \"...\"}}",
    "  ② 执行工具 → 获取 Observation（工具返回结果）",
    "  ③ Observation 反馈给 LLM → 再次 Think → 决定继续调工具 or 给 FinalAnswer",
    "  ④ 循环直到 {final_answer: \"...\"} 或达到 max_steps → 强制总结",
    "",
    "● 可用工具",
    "  ▸ nl2sql：自然语言→SQL→执行→返回结果",
    "  ▸ rag_search：四大名著知识库检索",
    "  ▸ graph_query：人物关系图谱查询",
    "  ▸ 工具注册在 ToolRegistry，LLM 自主选择调用哪个 + 传什么参数",
])
add_principle_box(slide, "ReAct 推理链",
    "用户：\"成绩最高的学生在哪个班级\" → Thought: 需先查成绩表 → Action: nl2sql(\"SELECT ... ORDER BY score DESC LIMIT 1\") → Observation: \"张三, 软件工程2103班, 95分\" → Thought: 已获得足够信息 → FinalAnswer: \"成绩最高的学生是张三，在软件工程2103班，成绩为95分\"")
add_page_number(slide, 11)

# ============================================================
# Slide 12: Function Calling
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_title_bar(slide, "Function Calling 工具调用", "单例 ToolRegistry + LLM JSON 驱动 + 自动执行")
add_body(slide, [
    "● ToolRegistry（单例）",
    "  ▸ 注册 6 个工具：nl2sql / rag_search / graph_query / calculate / get_weather / get_fortune",
    "  ▸ 每个工具：name + description + params schema + 异步执行函数",
    "",
    "● 调用流程",
    "  ▸ intent ∈ {data_query, knowledge_question} → 启用 Function Calling 模式",
    "  ▸ LLM 收到消息 + 工具列表 → 返回 JSON: {\"tool\": \"nl2sql\", \"params\": {\"query\": \"...\"}}",
    "  ▸ ToolRegistry.execute(name, params) → 结果反馈 LLM → 最多 3 轮工具调用",
    "  ▸ LLM 不需要工具时直接回复（不返回 JSON 即视为直接回答）",
    "  ▸ 其他 intent 走原有路由逻辑（完全不变）",
])
add_highlight_box(slide, "工具注册与调度",
    "单例 ToolRegistry 初始化时预注册全部工具函数（import 时延迟加载 Service 以避免循环依赖）。LLM system prompt 动态拼接可用工具列表。JSON 解析失败时降级为直接回复。calculate 工具使用 Python AST 安全解析数学表达式（仅允许 +-*/**，禁止任意代码执行）。",
    top=5.8)
add_page_number(slide, 12)

# ============================================================
# Slide 13: UI/UX 设计
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_title_bar(slide, "UI/UX 设计系统", "古典四大名著主题 + 现代交互体验")
add_body(slide, [
    "● 古典色彩系统",
    "  ▸ CSS 变量体系：朱红 #C43B3B / 黛蓝 #1B2A4A / 宣纸黄 #F5E6C8 / 金色 #C9A96E",
    "  ▸ 排版：楷体标题 + 微软雅黑正文，印章按钮/奏折表格/匾额头部/卷轴弹窗 mixins",
    "  ▸ Element Plus 全局 CSS 变量覆盖（:root 中 60+ 变量全部重定义为古典色值）",
    "",
    "● 交互升级",
    "  ▸ TabBar 标签页栏：打开页面自动添加标签，右键关闭，切换带 fade-slide 动画",
    "  ▸ 语音输入：MediaRecorder API → 后端 ASR → 自动填入输入框（红色脉冲录音动画）",
    "  ▸ 语音输出：浏览器 Web Speech API 降级（零配置）+ 后端 TTS（可选阿里云 Key）",
    "  ▸ 主动消息推送：SSE 每 15 秒检测 → 6 种触发类型 → 金色边框 + 主动搭话角标",
])
add_highlight_box(slide, "零外部依赖降级方案",
    "VoiceInput 录音优先使用 MediaRecorder API → 后端 ASR（阿里云 DashScope）。VoiceOutput 朗读优先使用浏览器 SpeechSynthesis API（内置、免费、零延迟）→ 后端 TTS 为备选。TTS/ASR 不可用时自动降级，核心对话功能完全不受影响。",
    top=5.8)
add_page_number(slide, 13)

# ============================================================
# Slide 14: 总结 & 展望
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_title_bar(slide, "总结 & 展望", "技术栈清单 + 已实现功能矩阵 + 未来方向")
add_body(slide, [
    "● 已实现技术亮点汇总",
    "  ▸ NL2SQL：自然语言→SQL→安全校验→执行→口语回答  ▸ 贝叶斯+LLM 混合意图分类",
    "  ▸ RAG 检索增强生成（四书分库 + 自动/原文/图谱/融合四模式）",
    "  ▸ 多智能体协同（TaskDecomposer + asyncio.gather + LLM merge）",
    "  ▸ ReAct 推理循环（Thought→Action→Observation→LLM自主工具调用）",
    "  ▸ Function Calling（ToolRegistry + JSON 驱动）",
    "  ▸ 三层记忆系统（fire-and-forget 提取 + Jaccard 去重 + MySQL/Milvus 双写）",
    "  ▸ BKT 贝叶斯知识追踪 + 薄弱点诊断 + LLM 学习计划",
    "  ▸ Neo4j 因果链推理 + 阵营分析 + 深度问答",
    "  ▸ 古典 CSS 主题系统 + TabBar + 语音交互 + 主动消息推送",
    "",
    "● 未来展望",
    "  ▸ 多模态：图像识别 + 文档 OCR  ▸ 知识图谱：自动从文本抽取事件和关系",
    "  ▸ 移动端：UniApp 适配  ▸ 数据安全：差分隐私 + 联邦学习",
])
add_page_number(slide, 14)

# ============================================================
# 保存
# ============================================================
output = "D:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/答辩PPT.pptx"
prs.save(output)
print(f"PPT saved to: {output}")
print(f"Total slides: {len(prs.slides)}")
