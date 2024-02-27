from core.data.models import Singleton, Connection
from sqlmodel import Field, Session, SQLModel, create_engine, select
from core.data.models import (
    UserModel,
    MessageModel,
    SectionModel,
    ChatModel,
    CourseModel,
    FeedbackModel,
    DevsModel
)
from core.utils import build_model_from_params

def message_oldformat_to_new(a_message : MessageModel | dict):
    if (isinstance(a_message, MessageModel)):
        return a_message
    message_new =  {
        "role": a_message["role"],
        "content": a_message["content"],
        "chat_key": a_message["chat"],
        "clear_number": a_message["clear_number"],
        "credential_token": a_message["credential_token"]
    }
    if a_message.get("message_id") is not None:
        message_new["mes_id"] = a_message.get("message_id")
    return MessageModel(**message_new)

class DataBase(metaclass=Singleton):
    def __init__(self) -> None:
        print("Initializing DataBase")
        self.connection = Connection()
    
    def insert_user(self, user : UserModel):
        """Insert User Based on Mixin Flask Object

        Args:
            user (User : UserFlaskMixin): user object
        """
        with self.connection.session() as session:
            session.add(user)
            session.commit()
            return user, session
    
    def insert_message(self, message : MessageModel | dict) -> tuple[MessageModel, Session]:
        if isinstance(message, MessageModel) is False:
            message : MessageModel = message_oldformat_to_new(message)
        with self.connection.session() as session:
            session.add(message)
            session.commit()
            session.refresh(message)
            session.expunge_all()
            return message, session
    
    def insert_chat(self, chat : ChatModel | str):
        if isinstance(chat, ChatModel) is False:
            if (chat == "none"):
                chat = ChatModel()
            else:
                chat = ChatModel(chat_id=chat)
        with self.connection.session() as session:
            session.add(chat)
            session.commit()
            return chat.chat_id, session
    
    @build_model_from_params(from_keys=["content", "message_id", "feedback_id"], model=FeedbackModel, is_method=True)
    def insert_feedback(self, *args, **kwargs) -> tuple[FeedbackModel, Session]:
        with self.connection.session() as session:
            session.add(args[0])
            session.commit()
            session.refresh(args[0])
            session.expunge_all()
            return args[0], session

    
    @build_model_from_params(from_keys=["course_id", "name", "proffessor", "mainpage", "collectionname"], model=CourseModel, is_method=True)
    def insert_course(self, *args, **kwargs) -> tuple[CourseModel, Session]:
        with self.connection.session() as session:
            session.add(args[0])
            session.commit()
            session.refresh(args[0])
            session.expunge_all()
            return args[0], session

    
    @build_model_from_params(from_keys=["section_id", "pulling_from", "sectionurl"], model=SectionModel, is_method=True)
    def insert_section(self, *args, **kwargs) -> tuple[SectionModel, Session]:
        with self.connection.session() as session:
            print("INSERTING SECTION: ")
            print(args[0])
            session.add(args[0])
            session.commit()
            session.refresh(args[0])
            session.expunge_all()
            return args[0], session
         
    def get_users_by_email(self, email : str):
        """Gets users by email

        Args:
            email (str): email
        """
        with self.connection.session() as session:
            statement = select(UserModel).where(UserModel.email == email)
            results = session.exec(statement).all()
            session.expunge_all()
            return results, session
    
    def get_users_by_id(self, uid : str):
        """Gets users by id

        Args:
            uid (str): uid
        """
        with self.connection.session() as session:
            statement = select(UserModel).where(UserModel.user_id == uid)
            results = session.exec(statement).all()
            session.expunge_all()
            return results, session
    
    def insert_user_to_course(self, user_id : str, course_id):
        with self.connection.session() as session:
            user = session.exec(select(UserModel).where(UserModel.user_id == user_id)).one()
            course = session.exec(select(CourseModel).where(CourseModel.course_id == course_id)).one()
            user.courses.append(course)
            session.add(user)
            session.commit()
            return user, course, session
    
    def establish_course_section_relationship(self, section_id: str, course_id: str):
        with self.connection.session() as session:
            section = session.exec(select(SectionModel).where(SectionModel.section_id == section_id)).one()
            course = session.exec(select(CourseModel).where(CourseModel.course_id == course_id)).one()
            section.courses.append(course)
            session.add(section)
            session.commit()
            return section, course, session

    def get_user_courses(self, user_id : str):
        with self.connection.session() as session:
            user = session.exec(select(UserModel).where(UserModel.user_id == user_id)).one()
            return user.courses, session

    def get_user_by_email_courses(self, email : str):
        with self.connection.session() as session:
            user = session.exec(select(UserModel).where(UserModel.email == email)).one()
            return user.courses, session
    
    def get_courses_sections(self, course_id):
        with self.connection.session() as session:
            course = session.exec(select(CourseModel).where(CourseModel.course_id == course_id)).one()
            return course.sections, session
    
    def get_courses_sections_format(self, course_id):
        with self.connection.session() as session:
            course = session.exec(select(CourseModel).where(CourseModel.course_id == course_id)).one()
            name = course.name
            result = [
                {
                    "section_id": section.section_id,
                    "course_id": course_id,
                    "section_url": section.sectionurl,
                    "pullingfrom": section.pulling_from,
                    "course_chroma_collection": name,
                }
                for section in course.sections
            ]
            return result, session

    def get_sections_by_id(self, section_id):
        with self.connection.session() as session:
            sections = session.exec(select(SectionModel).where(SectionModel.section_id == section_id)).all()
            return sections, session
        
        
    def update_section_add_fromdoc(self, section_id: str, from_doc):
        with self.connection.session() as session:
            section = session.exec(select(SectionModel).where(SectionModel.section_id == section_id)).one()
            section.pulling_from = section.pulling_from + "$" + from_doc
            session.add(section)
            session.commit()
            session.refresh(section)
            return section, session
        
    def all_messages(self):
        with self.connection.session() as session:
            stmt = select(MessageModel).order_by(MessageModel.chat_key).order_by(MessageModel.time_created)
            result = session.exec(stmt).all()
            return result
    