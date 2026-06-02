"""
朴素贝叶斯意图分类器
训练数据: conversation_history 表 → 种子关键词兜底
分类: MultinomialNB + TF-IDF
自我学习: 累计 20 条新样本后自动重训练
"""
import logging
import re
from typing import Tuple, List
from collections import defaultdict

logger = logging.getLogger(__name__)

# 种子关键词（conversation_history 无数据时使用）
SEED_KEYWORDS = {
    "data_query": ["查", "成绩", "学生", "班级", "就业", "课程", "多少", "统计", "排名", "数据", "考勤"],
    "knowledge_question": ["孙悟空", "猪八戒", "三国", "曹操", "红楼梦", "水浒", "西游", "林黛玉",
                           "诸葛亮", "大闹天宫"],
    "chat_greet": ["你好", "嗨", "你是谁", "叫什么", "再见", "谢谢", "早上好", "晚上好"],
    "emotional_support": ["难过", "伤心", "压力", "焦虑", "崩溃", "孤独", "失恋", "想哭", "郁闷"],
    "social_help": ["情书", "搭讪", "恋爱", "表白", "约会", "社交", "聊天", "怎么追"],
    "game_riddle": ["灯谜", "谜题", "猜谜", "谜语", "出题"],
    "game_poetry": ["对诗", "飞花令", "诗句", "诗词"],
    "weather_query": ["天气", "下雨", "温度", "刮风", "晴天", "阴天", "降温"],
    "fortune_telling": ["运势", "算命", "占卜", "运气", "卦"],
}

# 缓冲区
_training_buffer: List[Tuple[str, str]] = []


class BayesianClassifier:
    """朴素贝叶斯意图分类器"""

    def __init__(self):
        self._vectorizer = None
        self._model = None
        self._intents: List[str] = []
        self._trained = False
        self._load_data_and_train()

    def classify(self, message: str) -> Tuple[str, float]:
        """分类一条消息，返回 (intent, confidence)"""
        if not self._trained:
            return "unknown", 0
        try:
            x = self._vectorizer.transform([message])
            probs = self._model.predict_proba(x)[0]
            idx = probs.argmax()
            return self._model.classes_[idx], float(probs[idx])
        except Exception as e:
            logger.warning("Bayesian classify failed: %s", e)
            return "unknown", 0

    def add_sample(self, message: str, intent: str):
        """添加训练样本到缓冲区，累计 20 条后重训练"""
        if intent == "unknown" or not message or not message.strip():
            return
        _training_buffer.append((message.strip(), intent))
        if len(_training_buffer) >= 20:
            self._retrain()

    def _retrain(self):
        """增量重训练"""
        try:
            self._load_data_and_train()
            logger.info("Bayesian retrained with %d new samples", len(_training_buffer))
            _training_buffer.clear()
        except Exception as e:
            logger.error("Bayesian retrain failed: %s", e)

    def _load_data_and_train(self):
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.naive_bayes import MultinomialNB
        except ImportError:
            logger.warning("scikit-learn not installed, Bayesian classifier disabled")
            return

        texts, labels = self._collect_samples()

        if len(texts) < 3:
            return

        self._vectorizer = TfidfVectorizer(
            analyzer="char_wb", ngram_range=(1, 3), max_features=5000)
        x = self._vectorizer.fit_transform(texts)
        self._model = MultinomialNB(alpha=0.1)
        self._model.fit(x, labels)
        self._intents = list(self._model.classes_)
        self._trained = True
        logger.info("Bayesian classifier trained: %d samples, %d intents",
                     len(texts), len(self._intents))

    def _collect_samples(self) -> Tuple[List[str], List[str]]:
        """收集训练样本：DB + 种子关键词 + 缓冲区"""
        texts, labels = [], []

        # 1. 从 conversation_history 读取
        try:
            from backend.database import SessionLocal
            db = SessionLocal()
            from backend.entity.conversation_history import ConversationHistory
            rows = db.query(
                ConversationHistory.content,
                ConversationHistory.agent_type,
            ).filter(
                ConversationHistory.role == "user",
            ).order_by(ConversationHistory.id.desc()).limit(200).all()
            db.close()

            for content, agent_type in rows:
                intent = _agent_to_intent(agent_type)
                if intent and content:
                    texts.append(content)
                    labels.append(intent)
        except Exception as e:
            logger.warning("DB load for Bayesian failed: %s", e)

        # 2. 种子关键词兜底
        if len(texts) == 0:
            for intent, keywords in SEED_KEYWORDS.items():
                for kw in keywords:
                    texts.append(kw)
                    labels.append(intent)

        # 3. 缓冲区的增量样本
        for msg, intent in _training_buffer:
            texts.append(msg)
            labels.append(intent)

        return texts, labels


def _agent_to_intent(agent_type: str) -> str:
    """Agent 名称 → 意图代码"""
    if not agent_type:
        return ""
    mapping = {
        "BusinessManagementAgent": "data_query",
        "RAGKnowledgeAgent": "knowledge_question",
        "EmotionalCounselingAgent": "emotional_support",
        "SocialAssistantAgent": "social_help",
        "GameAgent": "game_riddle",
        "WeatherQueryAgent": "weather_query",
        "FortuneTellingAgent": "fortune_telling",
        "BajiePersonaAgent": "chat_greet",
        "LuzhishenPersonaAgent": "chat_greet",
        "LindaiyuPersonaAgent": "chat_greet",
        "ZhugeliangPersonaAgent": "chat_greet",
        "PersonaAgent": "chat_greet",
    }
    return mapping.get(agent_type, "")


# 全局单例
_classifier = None


def get_classifier() -> BayesianClassifier:
    global _classifier
    if _classifier is None:
        _classifier = BayesianClassifier()
    return _classifier


def add_training_sample(message: str, intent: str):
    """对外接口：添加训练样本"""
    get_classifier().add_sample(message, intent)


def classify(message: str) -> Tuple[str, float]:
    """对外接口：分类"""
    return get_classifier().classify(message)
