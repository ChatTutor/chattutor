from core.data.models import Singleton, Connection
from sqlmodel import Field, Session, SQLModel, create_engine, select
from core.data.models import (
    UserModel,
    MessageModel,
    SectionModel,
    ChatModel,
    CourseModel,
    FeedbackModel
)
from core.utils import build_model_from_params
import flask_login
import bcrypt

class User(flask_login.UserMixin):
    username = "NO FACE"
    email = "NO NAME"
    password_hash = "NO NUMBER"
    user_type = ""

    def get_id(self):
        return self.username

    @property
    def password(self):
        raise AttributeError("password not readable")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8", "ignore"), bcrypt.gensalt()
        )

    def verify_password(self, p):
        print(
            self.password_hash,
            bcrypt.hashpw(p.encode("utf8", "ignore"), bcrypt.gensalt()).decode("utf-8"),
        )
        print(
            self.password_hash,
            bcrypt.hashpw(p.encode("utf8", "ignore"), bcrypt.gensalt()).decode("utf-8"),
        )
        print(self.password_hash.encode("utf-8"), p.encode("utf-8"))
        return bcrypt.checkpw(p.encode("utf-8"), self.password_hash.encode("utf-8"))


def user_to_model(user: User):
    return UserModel(username=user.username, email=user.email, password=user.password_hash.decode('utf-8'), user_type=user.user_type)

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
    
    def insert_user(self, user : User):
        """Insert User Based on Mixin Flask Object

        Args:
            user (User : UserFlaskMixin): user object
        """
        with self.connection.session() as session:
            user_model = user_to_model(user=user)
            session.add(user_model)
            session.commit()
            return user_model, session
    
    def insert_message(self, message : MessageModel | dict) -> tuple[MessageModel, Session]:
        if isinstance(message, MessageModel) is False:
            message : MessageModel = message_oldformat_to_new(message)
        with self.connection.session() as session:
            session.add(message)
            session.commit()
            return message, session
    
    def insert_chat(self, chat : ChatModel | str):
        if isinstance(chat, ChatModel) is False:
            chat = ChatModel(chat_id=chat)
        with self.connection.session() as session:
            session.add(chat)
            session.commit()
            return chat, session
    
    @build_model_from_params(from_keys=["content", "message_id", "feedback_id"], model=FeedbackModel, is_method=True)
    def insert_feedback(self, *args, **kwargs) -> tuple[FeedbackModel, Session]:
        with self.connection.session() as session:
            session.add(args[0])
            session.commit()
            return args[0], session

    
    @build_model_from_params(from_keys=["course_id", "name", "proffessor", "mainpage", "collectionname"], model=CourseModel, is_method=True)
    def insert_course(self, *args, **kwargs) -> tuple[CourseModel, Session]:
        with self.connection.session() as session:
            session.add(args[0])
            session.commit()
            return args[0], session

    
    @build_model_from_params(from_keys=["section_id", "pulling_from", "sectionurl"], model=SectionModel, is_method=True)
    def insert_section(self, *args, **kwargs) -> tuple[SectionModel, Session]:
        with self.connection.session() as session:
            print("INSERTING SECTION: ")
            print(args[0])
            session.add(args[0])
            session.commit()
            return args[0], session
         
    def get_users_by_username(self, username : str):
        """Gets users by username

        Args:
            username (str): username
        """
        with self.connection.session() as session:
            statement = select(UserModel).where(UserModel.username == username)
            results = session.exec(statement).all()
            return results, session
    
    def insert_user_to_course(self, username : str, course_id):
        with self.connection.session() as session:
            user = session.exec(select(UserModel).where(UserModel.username == username)).one()
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

    def get_user_courses(self, username : str):
        with self.connection.session() as session:
            user = session.exec(select(UserModel).where(UserModel.username == username)).one()
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
    