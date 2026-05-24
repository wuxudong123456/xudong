"""
实体层模块初始化
"""
from backend.entity.base import Base
from backend.entity.teacher import Teacher
from backend.entity.class_info import ClassInfo
from backend.entity.student import Student
from backend.entity.score import Score
from backend.entity.employment import Employment
from backend.entity.user import User
from backend.entity.course import Course
from backend.entity.operation_log import OperationLog
from backend.entity.qa_pair import QAPair
from backend.entity.document_chunk import DocumentChunk
from backend.entity.conversation_history import ConversationHistory
from backend.entity.lantern_riddle import LanternRiddle
from backend.entity.permission import Permission, RolePermission

__all__ = [
    "Base", "Teacher", "ClassInfo", "Student", "Score",
    "Employment", "User", "Course", "OperationLog",
    "QAPair", "DocumentChunk", "ConversationHistory",
    "LanternRiddle", "Permission", "RolePermission",
]
