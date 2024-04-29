from typing import List
from sqlalchemy import func

from sqlalchemy import delete
import json
from sqlalchemy.orm import joinedload

from core.data.models import Singleton, Connection, User
from sqlmodel import Field, Session, SQLModel, create_engine, select, Sequence
from core.data.models import (
    UserModel,
    MessageModel,
    SectionModel,
    ChatModel,
    CourseModel,
    FeedbackModel,
    DevsModel,
    VerificationCodeModel,
    ResetCode,
    MessageCourseLink,
    MessageUserLink,
)
from core.data.models.AccessCodes import AccessCodeModel
from core.data.models.ResetCode import ResetCodeModel
from core.utils import build_model_from_params
from sqlalchemy.exc import IntegrityError


def message_from_joined(message, user, uuser, c, feeds):
    print("U S E R")
    print(user)
    message.update(
        {
            "user_id": user.get("user_id", "LOGGED_OUT"),
            "user_email": uuser.get("email", "LOGGED_OUT"),
            "feedbacks": [x for x in json.loads(f"[{feeds}]") if x["content"] != None],
            "course_id": c["course_id"],
        }
    )
    return message


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

    def insert_message(
        self, message: MessageModel | dict, course_collname=None, user_id=None
    ) -> tuple[MessageModel, Session, List]:
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
            # session.refresh(message)

            if user_id is not None:
                stmt = select(UserModel).where(UserModel.user_id == user_id)
                usr = session.exec(stmt).first()
                if usr is not None:
                    usr.messages.append(message)
                    session.commit()
                    session.refresh(message)
                    session.refresh(usr)

            if course_collname is not None:
                stmt = select(CourseModel).where(CourseModel.collectionname == course_collname)
                course = session.exec(stmt).one()
                course.messages.append(message)
                session.commit()
                session.refresh(course)
                session.refresh(message)

            # session.refresh(message)
            session.expunge_all()
            return message, session, ["usr"]

    def insert_access_code(
        self, access_code: AccessCodeModel | str
    ) -> tuple[AccessCodeModel, Session]:
        with Connection().session() as session:
            existing_ = session.exec(
                select(AccessCodeModel).where(AccessCodeModel.id == access_code.id)
            ).first()
            if existing_ is not None:
                existing_.code = access_code.code
                existing_.email = access_code.email
                session.commit()
                session.refresh(existing_)
                session.expunge_all()
                return access_code.jsonserialize(), session
            else:
                session.add(access_code)
                session.commit()
                session.refresh(access_code)
                session.expunge_all()
                return access_code.jsonserialize(), session

    def remove_acces_code(self, code: str, uid: str):
        with Connection().session() as session:
            stmt = (
                delete(AccessCodeModel)
                .where(AccessCodeModel.code == code)
                .where(AccessCodeModel.id == uid)
            )
            print("statement", stmt)
            existing_ = session.exec(stmt)
            session.commit()

    def get_acces_code(self, code: str, uid: str) -> tuple[AccessCodeModel, Session]:
        with Connection().session() as session:
            stmt = (
                select(AccessCodeModel)
                .where(AccessCodeModel.code == code)
                .where(AccessCodeModel.id == uid)
            )
            existing_ = session.exec(stmt).first()
            session.expunge_all()
            if existing_:
                return existing_.jsonserialize(), session
            return None, session

    def get_access_code_by_code(self, code: str) -> tuple[AccessCodeModel, Session]:
        with Connection().session() as session:
            existing_ = session.exec(
                select(AccessCodeModel).where(AccessCodeModel.code == code)
            ).first()
            session.expunge_all()
            return existing_.jsonserialize(), session

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
        from_keys=["id", "user_id"],
        model=VerificationCodeModel,
        is_method=True,
    )
    def insert_verif(self, *args, **kwargs) -> tuple[VerificationCodeModel, Session]:
        """Insert E-mail verification code
        Args:
            args[0] (VerificationCodeModel) : verification code object


        Returns:
            tuple[VerificationCodeModel, Session]: _description_
        """
        with Connection().session() as session:
            print("INSERTING VERIF: ")
            print(args[0])

            try:
                # Add the new_user object to the session
                session.add(args[0])
                # Commit the session to persist the changes
                session.commit()
                print("Verif added successfully.")
            except IntegrityError as e:
                session.rollback()
                print("Verif already exists or integrity constraint violation:", e)
                # Query the existing entry with the duplicate primary key
                existing_verif = session.exec(
                    select(VerificationCodeModel).where(
                        VerificationCodeModel.user_id == args[0].user_id
                    )
                ).one()
                if existing_verif:
                    # Update the attributes of the existing entry
                    existing_verif.id = args[0].id
                    existing_verif.user_id = args[0].user_id
                    # Commit the changes
                    session.commit()
                    print("Existing verif updated successfully.")
                else:
                    print("Existing verif not found.")

            return args[0], session

    @build_model_from_params(
        from_keys=["id", "code", "email"],
        model=ResetCodeModel,
        is_method=True,
    )
    def insert_reset_code(self, *args, **kwargs) -> tuple[ResetCodeModel, Session]:
        """Insert E-mail verification code
        Args:
            args[0] (VerificationCodeModel) : verification code object


        Returns:
            tuple[VerificationCodeModel, Session]: _description_
        """

        with Connection().session() as session:
            all_existing = session.exec(
                delete(ResetCodeModel).where(ResetCodeModel.email == args[0].email)
            )

            session.commit()

        with Connection().session() as session:
            print("INSERTING reset: ")
            print(args[0])

            try:
                # Add the new_user object to the session
                session.add(args[0])
                # Commit the session to persist the changes
                session.commit()
                print("Verif added successfully.")
            except IntegrityError as e:
                session.rollback()
                print("Verif already exists or integrity constraint violation:", e)
                # Query the existing entry with the duplicate primary key
                existing_verif = session.exec(
                    select(ResetCodeModel).where(ResetCodeModel.email == args[0].email)
                ).one()
                if existing_verif:
                    # Update the attributes of the existing entry
                    existing_verif.id = args[0].id
                    existing_verif.code = args[0].code
                    existing_verif.email = args[0].email
                    # Commit the changes
                    session.commit()
                    print("Existing verif updated successfully.")
                else:
                    print("Existing verif not found.")

            return args[0], session

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
            fd = args[0]
            print(fd)
            session.add(fd)
            session.commit()
            return fd.feedback_id, session

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

    # def enroll_user_to_course_by_id(
    #     self, user_id, course_id
    # ) -> tuple[UserModel, CourseModel, Session]:
    #     """Mark user as student of the specified course

    #     Args:
    #         user_id (str): user id
    #         course_id (str): course id

    #     Returns:
    #         tuple[UserModel, CourseModel, Session]: user, course, session
    #     """
    #     with Connection().session() as session:
    #         user = session.exec(select(UserModel).where(UserModel.user_id == user_id)).one()
    #         course = session.exec(
    #             select(CourseModel).where(CourseModel.course_id == course_id)
    #         ).one()
    #         user.studied_courses.append(course)
    #         session.add(user)
    #         session.commit()
    #         return user, course, session

    def enroll_user_to_course_by_collectionname(
        self, user_id, course_collectionname
    ) -> tuple[str, Session]:
        """Mark user as student of the specified course

        Args:
            user_id (str): user id
            course_collectionname (str): course collectionname

        Returns:
            tuple[UserModel, CourseModel, Session]: user, course, session
        """
        with Connection().session() as session:
            try:
                user = session.exec(select(UserModel).where(UserModel.user_id == user_id)).one()
                course = session.exec(
                    select(CourseModel).where(CourseModel.collectionname == course_collectionname)
                ).one()
                try:
                    if user.studied_courses.count(course) == 0:
                        user.studied_courses.append(course)
                        session.add(user)
                        session.commit()
                        mainpage = course.mainpage
                except IntegrityError as e:
                    print("[ERROR] User is already enrolled!!")
                    mainpage = course.mainpage
                    return mainpage, session
                mainpage = course.mainpage
                print(f"[SUCCESS] {mainpage}")
                return mainpage, session
            except:
                print("[ERROR] Something went wrong with enrolling user to course!!")
                return None, session

    # @build_model_from_params(
    #     from_keys=["section_id", "pulling_from", "sectionurl"],
    #     model=SectionModel,
    #     is_method=True,
    # )
    def insert_section(self, *args, **kwargs) -> tuple[SectionModel, Session]:
        """Insert course

        Returns:
            tuple[SectionModel, Session]: _description_
        """
        with Connection().session() as session:
            print("INSERTING SECTION: ")
            print(args[0])

            try:
                # Add the new_user object to the session
                session.add(args[0])
                # Commit the session to persist the changes
                session.commit()
                print("Section added successfully.")
            except IntegrityError as e:
                session.rollback()
                print("Section already exists or integrity constraint violation:", e)
                # Query the existing entry with the duplicate primary key
                existing_section = session.exec(
                    select(SectionModel).where(SectionModel.section_id == args[0].section_id)
                ).one()
                if existing_section:
                    # Update the attributes of the existing entry
                    existing_section.pulling_from = args[0].pulling_from
                    existing_section.sectionurl = args[0].sectionurl
                    existing_section.courses = args[0].courses
                    # Commit the changes
                    session.commit()
                    print("Existing user updated successfully.")
                else:
                    print("Existing user not found.")
            # session.add(args[0])
            # session.merge(args[0])
            # session.commit()
            # session.refresh(args[0])
            # session.expunge_all()
            return args[0], session

    def get_verif(self, code):
        with Connection().session() as session:
            statement = select(VerificationCodeModel).where(VerificationCodeModel.id == code)
            res = session.exec(statement).first()
            session.expunge_all()
            return res, session

    def get_reset_code(self, email, code):
        with Connection().session() as session:
            statement = select(ResetCodeModel).where(
                ResetCodeModel.email == email and ResetCodeModel.code == code
            )
            res = session.exec(statement).first()
            session.expunge_all()
            return res, session

    def get_all_courses_urls(self) -> list[str]:
        with Connection().session() as session:
            statement = select(CourseModel)
            res = session.exec(statement).all()
            urls = [x.mainpage for x in res]
            return urls

    def get_course_messages_by_user(self, user_id, course_id):
        with Connection().session() as session:
            statement = (
                select(
                    MessageModel,
                    MessageUserLink,
                    MessageCourseLink,
                    UserModel,
                    func.group_concat(
                        func.json_object(
                            "feedback_id",
                            FeedbackModel.feedback_id,
                            "message_id",
                            FeedbackModel.message_id,
                            "content",
                            FeedbackModel.content,
                        )
                    ).label("feedbacks"),
                )
                .join(
                    MessageUserLink,
                    MessageUserLink.message_id == MessageModel.mes_id,
                )
                .join(
                    MessageCourseLink,
                    MessageCourseLink.message_id == MessageModel.mes_id,
                )
                .outerjoin(FeedbackModel, FeedbackModel.message_id == MessageModel.mes_id)
                .outerjoin(UserModel, UserModel.user_id == MessageUserLink.user_id)
                .where(MessageUserLink.user_id == user_id)
                .where(MessageCourseLink.course_id == course_id)
                .group_by(MessageModel.mes_id)
            )
            res = session.exec(statement).all()
            messages_with_feedback_json = [
                (
                    message.jsonserialize(),
                    user.jsonserialize(),
                    c.jsonserialize(),
                    uuser.jsonserialize(),
                    feeds,
                )
                for message, user, c, uuser, feeds in res
            ]
            messages_with_feedback_json = [
                message_from_joined(message, user, uuser, c, feeds)
                for message, user, c, uuser, feeds in messages_with_feedback_json
            ]
            return messages_with_feedback_json, session

    def get_course_messages_2(self, course_id):
        with Connection().session() as session:
            statement = (
                select(
                    MessageModel,
                    MessageUserLink,
                    MessageCourseLink,
                    UserModel,
                    func.group_concat(
                        func.json_object(
                            "feedback_id",
                            FeedbackModel.feedback_id,
                            "message_id",
                            FeedbackModel.message_id,
                            "content",
                            FeedbackModel.content,
                        )
                    ).label("feedbacks"),
                )
                .join(
                    MessageUserLink,
                    MessageUserLink.message_id == MessageModel.mes_id,
                )
                .join(
                    MessageCourseLink,
                    MessageCourseLink.message_id == MessageModel.mes_id,
                )
                .outerjoin(FeedbackModel, FeedbackModel.message_id == MessageModel.mes_id)
                .outerjoin(UserModel, UserModel.user_id == MessageUserLink.user_id)
                .group_by(MessageUserLink.user_id)
                .where(MessageCourseLink.course_id == course_id)
                .group_by(MessageModel.mes_id)
            )
            res = session.exec(statement).all()
            messages_with_feedback_json = [
                (
                    message.jsonserialize(),
                    user.jsonserialize(),
                    c.jsonserialize(),
                    uuser.jsonserialize(),
                    feeds,
                )
                for message, user, c, uuser, feeds in res
            ]
            messages_with_feedback_json = [
                message_from_joined(message, user, uuser, c, feeds)
                for message, user, c, uuser, feeds in messages_with_feedback_json
            ]
            return messages_with_feedback_json, session

    def get_course_messages(self, course_id):
        with Connection().session() as session:
            statement = select(CourseModel).where(CourseModel.course_id == course_id)
            print("debug_exec statement:", statement)
            res = session.exec(statement).first()
            if res is None:
                return None, session

            msgs = [json.loads(x.json()) for x in res.messages]
            for message, mx in zip(msgs, res.messages):
                try:
                    message["user_email"] = json.loads(mx.users[0].json())["email"]
                    message["user_id"] = json.loads(mx.users[0].json())["user_id"]
                except:
                    message["user_email"] = "LOGGED_OUT"
                    message["user_id"] = "LOGGED_OUT"

            for message in msgs:
                message["feedbacks"] = []

            for message in msgs:
                m_id = message["mes_id"]
                statement = select(FeedbackModel).where(FeedbackModel.message_id == m_id)
                feed_res = session.exec(statement).all()
                feedbacks = [x.jsonserialize() for x in feed_res]
                for feedback in feedbacks:
                    message["feedbacks"].append(feedback)
                # message["_sa_instance_state"] = None

            print("MESSAGES [DEBUG]")
            return msgs, session

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

    def get_course_name_by_mainpage(self, course_mainpage) -> tuple[str, Session]:
        """Get course by specified mainpage url

        Args:
            course_mainpage (str): mainpage url

        Returns:
            tuple[str, Session]: collection name, and session
        """
        with Connection().session() as session:
            course = session.exec(
                select(CourseModel).where(CourseModel.mainpage == course_mainpage)
            ).one()
            return course.collectionname, session

    def get_course_name_by_sections_mainpage(self, course_mainpage) -> tuple[str, Session]:
        """Get course by specified mainpage url

        Args:
            course_mainpage (str): mainpage url

        Returns:
            tuple[str, Session]: collection name, and session
        """
        with Connection().session() as session:
            sect = session.exec(
                select(SectionModel).where(course_mainpage == SectionModel.sectionurl)
            ).first()
            if sect == None:
                return None, session
            if len(sect.courses) == None:
                return None, session
            course = sect.courses[0]
            if course == None:
                return None, session
            return course.collectionname, session

    def get_course_id_by_mainpage(self, course_mainpage) -> tuple[str, Session]:
        """Get course by specified mainpage url

        Args:
            course_mainpage (str): mainpage url

        Returns:
            tuple[str, Session]: collection id, and session
        """
        with Connection().session() as session:
            course = session.exec(
                select(CourseModel).where(CourseModel.mainpage == course_mainpage)
            ).one()
            return course.course_id, session

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

    def get_courses_students(self, course_id) -> tuple[list[UserModel], Session]:
        """Get courses students

        Args:
            course_id (str): course id

        Returns:
            tuple[list[SectionModel], Session]: sections and session
        """
        with Connection().session() as session:
            course = session.exec(
                select(CourseModel).where(CourseModel.course_id == course_id)
            ).one()
            return [s.jsonserialize() for s in course.students], session

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

    def get_one_section_by_id(self, section_id) -> tuple[SectionModel, Session]:
        """Get connections specified by an id

        Args:
            section_id (str): section id

        Returns:
            tuple[Sequence[SectionModel], Session]: sections and session
        """
        with Connection().session() as session:
            sections = session.exec(
                select(SectionModel).where(SectionModel.section_id == section_id)
            ).first()
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

    def verify_user(self, user_id: str) -> tuple[UserModel, Session]:
        """verifies a user by user_id

        Args:
            user_id (str): user_id

        Returns:
            tuple[UserModel, Session]: _description_
        """
        with Connection().session() as session:
            try:
                user = session.exec(select(UserModel).where(UserModel.user_id == user_id)).one()
                user.verified = "true"
                session.commit()
                session.expunge_all()
                return user, session
            except Exception as e:
                return None, session

    def reset_user_password(self, new_password: str, code: str) -> tuple[UserModel, Session]:
        with Connection().session() as session:
            print("Trying...")
            try:
                v_model = session.exec(
                    select(ResetCodeModel).where(ResetCodeModel.code == code)
                ).one()
                user = session.exec(select(UserModel).where(UserModel.email == v_model.email)).one()
                print("User email: ", user.email)
                user.password = new_password
                session.commit()
                session.expunge_all()
                return user, session
            except Exception as e:
                print(f"Exception! {e}: ", user.email)
                return None, session
