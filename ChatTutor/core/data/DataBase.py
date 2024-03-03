from core.data.models import Singleton, Connection
from sqlmodel import Field, Session, SQLModel, create_engine, select, Sequence
from core.data.models import (
    UserModel,
    MessageModel,
    SectionModel,
    ChatModel,
    CourseModel,
    FeedbackModel,
    DevsModel,
)
from core.utils import build_model_from_params


def message_oldformat_to_new(a_message: MessageModel | dict) -> MessageModel:
    """Change old format to new format on messages,
    if a dict is provided, or leaves the object unaffected and
    returns it if a MessageModel is proivded

    Args:
        a_message (MessageModel | dict): old message or MessageModel

    Returns:
        MessageModel: new format compliant message object build from the dict,
        or same MessageModel object if provided
    """
    if isinstance(a_message, MessageModel):
        return a_message
    message_new = {
        "role": a_message["role"],
        "content": a_message["content"],
        "chat_key": a_message["chat"],
        "clear_number": a_message["clear_number"],
        "credential_token": a_message["credential_token"],
    }
    if a_message.get("message_id") is not None:
        message_new["mes_id"] = a_message.get("message_id")
    return MessageModel(**message_new)


class DataBase(metaclass=Singleton):
    """## DataBase singleton

    Call as such:
        ```py
        DataBase().<method>
        ```
    Exposed Method-APIs:
    - insert_user
    - insert_message
    - insert_chat
    - insert_feedback
    - insert_course
    - insert_section
    - get_users_by_email
    - get_users_by_id
    - insert_user_to_course
    - establish_course_section_relationship
    - get_user_courses
    - get_user_by_email_courses
    - get_courses_sections
    - get_courses_sections_format
    - get_sections_by_id
    - update_section_add_fromdoc
    - all_messages

    Args:
        metaclass (_type_, optional): Defaults to Singleton.
    """

    def __init__(self) -> None:
        print("Initializing DataBase")

    def insert_user(self, user: UserModel):
        """Insert User

        Args:
            user (User : UserModel): user object
        """
        with Connection().session() as session:
            session.add(user)
            session.commit()
            return user, session

    def insert_message(self, message: MessageModel | dict) -> tuple[MessageModel, Session]:
        """Insert message in DataBase

        Args:
            message (MessageModel | dict): message

        Returns:
            tuple[MessageModel, Session]: message and session
        """
        if isinstance(message, MessageModel) is False:
            message: MessageModel = message_oldformat_to_new(message)
        with Connection().session() as session:
            session.add(message)
            session.commit()
            session.refresh(message)
            session.expunge_all()
            return message, session

    def insert_chat(self, chat: ChatModel | str) -> tuple[str, Session]:
        """Insert chat (id) into db

        Args:
            chat (ChatModel | str): chat_id

        Returns:
            tuple[any | str, Session]: chat id and session
        """
        if isinstance(chat, ChatModel) is False:
            if chat == "none":
                chat = ChatModel()
            else:
                chat = ChatModel(chat_id=chat)
        with Connection().session() as session:
            session.add(chat)
            session.commit()
            return chat.chat_id, session

    @build_model_from_params(
        from_keys=["content", "message_id", "feedback_id"],
        model=FeedbackModel,
        is_method=True,
    )
    def insert_feedback(self, *args, **kwargs) -> tuple[FeedbackModel, Session]:
        """Insert feedback
        Args:
            feedback (FeedbackModel) : feedback

        Returns:
            tuple[FeedbackModel, Session]: _description_
        """
        with Connection().session() as session:
            session.add(args[0])
            session.commit()
            session.refresh(args[0])
            session.expunge_all()
            return args[0], session

    @build_model_from_params(
        from_keys=["course_id", "name", "proffessor", "mainpage", "collectionname"],
        model=CourseModel,
        is_method=True,
    )
    def insert_course(self, *args, **kwargs) -> tuple[CourseModel, Session]:
        """Insert course

        Returns:
            tuple[CourseModel, Session]: _description_
        """
        with Connection().session() as session:
            session.add(args[0])
            session.commit()
            session.refresh(args[0])
            session.expunge_all()
            return args[0], session

    @build_model_from_params(
        from_keys=["section_id", "pulling_from", "sectionurl"],
        model=SectionModel,
        is_method=True,
    )
    def insert_section(self, *args, **kwargs) -> tuple[SectionModel, Session]:
        """Insert course

        Returns:
            tuple[SectionModel, Session]: _description_
        """
        with Connection().session() as session:
            print("INSERTING SECTION: ")
            print(args[0])
            session.add(args[0])
            session.commit()
            session.refresh(args[0])
            session.expunge_all()
            return args[0], session

    def get_users_by_email(self, email: str):
        """Gets users by email

        Args:
            email (str): email
        """
        with Connection().session() as session:
            statement = select(UserModel).where(UserModel.email == email)
            results = session.exec(statement).all()
            session.expunge_all()
            return results, session

    def get_users_by_id(self, uid: str):
        """Gets users by id

        Args:
            uid (str): uid
        """
        with Connection().session() as session:
            statement = select(UserModel).where(UserModel.user_id == uid)
            results = session.exec(statement).all()
            session.expunge_all()
            return results, session

    def insert_user_to_course(
        self, user_id: str, course_id
    ) -> tuple[UserModel, CourseModel, Session]:
        """Make user as owner of the specified course

        Args:
            user_id (str): user id
            course_id (str): course id

        Returns:
            tuple[UserModel, CourseModel, Session]: user, course, session
        """
        with Connection().session() as session:
            user = session.exec(select(UserModel).where(UserModel.user_id == user_id)).one()
            course = session.exec(
                select(CourseModel).where(CourseModel.course_id == course_id)
            ).one()
            user.courses.append(course)
            session.add(user)
            session.commit()
            return user, course, session

    def establish_course_section_relationship(
        self, section_id: str, course_id: str
    ) -> tuple[SectionModel, CourseModel, Session]:
        """Add section to course

        Args:
            section_id (str): section_id
            course_id (str): course_id

        Returns:
            _type_: _description_
        """
        with Connection().session() as session:
            section = session.exec(
                select(SectionModel).where(SectionModel.section_id == section_id)
            ).one()
            course = session.exec(
                select(CourseModel).where(CourseModel.course_id == course_id)
            ).one()
            section.courses.append(course)
            session.add(section)
            session.commit()
            return section, course, session

    def get_user_courses(self, user_id: str) -> tuple[list[CourseModel], Session]:
        """Get user courses

        Args:
            user_id (str): user id

        Returns:
            tuple[list[CourseModel], Session]: courses and session
        """
        with Connection().session() as session:
            user = session.exec(select(UserModel).where(UserModel.user_id == user_id)).one()
            return user.courses, session

    def get_user_by_email_courses(self, email: str) -> tuple[list[CourseModel], Session]:
        """Get user courses specified by email

        Args:
            email (str): user email

        Returns:
            tuple[list[CourseModel], Session]: courses and session
        """
        with Connection().session() as session:
            user = session.exec(select(UserModel).where(UserModel.email == email)).one()
            return user.courses, session

    def get_courses_sections(self, course_id) -> tuple[list[SectionModel], Session]:
        """Get courses sections

        Args:
            course_id (str): course id

        Returns:
            tuple[list[SectionModel], Session]: sections and session
        """
        with Connection().session() as session:
            course = session.exec(
                select(CourseModel).where(CourseModel.course_id == course_id)
            ).one()
            return course.sections, session

    def validate_course_owner(self, collectionname: str, user_email: str) -> bool:
        """_summary_

        Args:
            collectionname (str): _description_
            user_email (str): _description_
        """
        with Connection().session() as session:
            course = session.exec(
                select(CourseModel).where(CourseModel.collectionname == collectionname)
            ).one()
            users_emails = [u.email for u in course.users]
            if user_email in users_emails:
                return True
            return False

    def get_courses_sections_format(self, course_id) -> tuple[list, Session]:
        """Get sections of course and format in old format

        Args:
            course_id (str): course id

        Returns:
            tuple[list[dict | any], Session]: sections and session
        """
        with Connection().session() as session:
            course = session.exec(
                select(CourseModel).where(CourseModel.course_id == course_id)
            ).one()
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

    def get_sections_by_id(self, section_id) -> tuple[Sequence[SectionModel], Session]:
        """Get connections specified by an id

        Args:
            section_id (str): section id

        Returns:
            tuple[Sequence[SectionModel], Session]: sections and session
        """
        with Connection().session() as session:
            sections = session.exec(
                select(SectionModel).where(SectionModel.section_id == section_id)
            ).all()
            return sections, session

    def update_section_add_fromdoc(self, section_id: str, from_doc) -> tuple[SectionModel, Session]:
        """Add from_doc to section's pulling_from which specifies which urls the section
        allows a tutor to know about.

        Args:
            section_id (str): section id
            from_doc (_type_): regex standardified url (_ replaces all punctuation) of the page

        Returns:
            tuple[SectionModel, Session]: section and session
        """
        with Connection().session() as session:
            section = session.exec(
                select(SectionModel).where(SectionModel.section_id == section_id)
            ).one()
            section.pulling_from = section.pulling_from + "$" + from_doc
            session.add(section)
            session.commit()
            session.refresh(section)
            return section, session

    def all_messages(self) -> Sequence[MessageModel]:
        """Get all messages ever sent by all users

        Returns:
            Sequence[MessageModel]: all messages
        """
        with Connection().session() as session:
            stmt = (
                select(MessageModel)
                .order_by(MessageModel.chat_key)
                .order_by(MessageModel.time_created)
            )
            result = session.exec(stmt).all()
            return result
