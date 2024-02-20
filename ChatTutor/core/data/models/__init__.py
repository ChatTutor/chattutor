import os
from core.data.models.UserCourseLink import UserCourseLink
from core.data.models.SectionCourseLink import SectionCourseLink
from core.data.models.Course import Course as CourseModel
from core.data.models.Chat import Chat as ChatModel
from core.data.models.Message import Message as MessageModel
from core.data.models.Section import Section as SectionModel
from core.data.models.User import User as UserModel
from core.data.models.Feedback import Feedback as FeedbackModel

from sqlmodel import create_engine, SQLModel
from core.data.models.connect import Connection, Singleton