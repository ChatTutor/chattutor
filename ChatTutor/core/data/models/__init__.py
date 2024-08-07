import os
from core.data.models.UserCourseLink import UserCourseLink
from core.data.models.SectionCourseLink import SectionCourseLink
from core.data.models.Course import Course as CourseModel
from core.data.models.Chat import Chat as ChatModel
from core.data.models.Message import Message as MessageModel
from core.data.models.Section import Section as SectionModel
from core.data.models.User import User as UserModel
from core.data.models.Feedback import Feedback as FeedbackModel
from core.data.models.Devs import Devs as DevsModel
from core.data.models.VerificationCode import VerificationCode as VerificationCodeModel
from sqlmodel import create_engine, SQLModel
from core.data.models.connect import Connection, Singleton
from core.data.models.MessageCourseLink import MessageCourseLink
from core.data.models.MessageUserLink import MessageUserLink
