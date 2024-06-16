from typing import List

import pymysql.err
import sqlalchemy.exc
from sqlalchemy import func, outerjoin
from sqlalchemy import text

from sqlalchemy import delete
import json
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
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
from core.data.models.Author import Author
from core.data.models.PublicationAuthorLink import PublicationAuthorLink
from core.data.models.Publication import Publication
from core.data.models.Citations import Citations
from core.data.models.PublicationCitationLink import PublicationCitationLink
from core.data.models.ResetCode import ResetCodeModel
from core.utils import build_model_from_params
from core.natlang import to_sql_match
from sqlalchemy.exc import IntegrityError
import re
from sqlalchemy.sql import union_all


def extract_sql_text(text):
    match = re.search(r"```sql\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return None


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

    def safe_exec(self, query):
        if (
            "SELECT" in query
            and (not "DELETE" in query)
            and (not "INSERT" in query)
            and (not "UPDATE" in query)
        ):
            try:

                query = extract_sql_text(query)
                if query == None:
                    return {"error": "Invalid query!"}, False
                # try:
                with Connection().session() as session:
                    result = session.exec(text(query)).mappings().all()
                    return result, session
            except:
                return {"error": "Invalid query, try again!"}, False

        # except:
        # return {"error": "Invalid query!"}, False
        else:
            return {"error": "Unsafe query!"}, False

    def insert_user(self, user: UserModel):
        """Insert User

        Args:
            user (User : UserModel): user object
        """
        with Connection().session() as session:
            session.add(user)
            session.commit()
            return user, session

    def insert_paper(self, model: Publication, citations: List[Citations], authors: List[Author]):
        resid = model.result_id
        with Connection().session() as session:

            print(f"\n\n\nINSERT PAPER:: {model}\n\n\n")
            existing_pap = session.query(Publication).filter_by(result_id=resid).first()
            if not existing_pap:
                session.add(model)
                session.commit()

        # for cit in citations:
        #     ciid = cit.citation_id
        #     with Connection().session() as session:
        #         session.add(cit)
        #         try:
        #             session.commit()
        #         except pymysql.err.IntegrityError:
        #             print("[Already]")
        #         except sqlalchemy.exc.IntegrityError:
        #             print("[Already]")
        #     with Connection().session() as session:
        #         link = PublicationCitationLink(citation_id=ciid, publication_id=resid)
        #         # session.refresh(link)
        #         session.add(link)
        #         try:
        #             session.commit()
        #         except pymysql.err.IntegrityError:
        #             print("[Already]")
        #         except sqlalchemy.exc.IntegrityError:
        #             print("[Already]")

        auids = []

        with Connection().session() as session:
            for au_ind in range(0, len(authors)):
                au = authors[au_ind]

                auid = au.author_id
                auids.append(auid)
                existing_author = session.query(Author).filter_by(author_id=auid).first()
                if not existing_author:
                    session.add(au)
            session.commit()

        with Connection().session() as session:
            for auid in auids:
                link = PublicationAuthorLink(author_id=auid, publication_id=resid)
                existing_link = (
                    session.query(PublicationAuthorLink)
                    .filter_by(author_id=auid, publication_id=resid)
                    .first()
                )
                if not existing_link:
                    session.add(link)
            session.commit()

    def get_author_by_name_like(self, name_like):
        with Connection().session() as session:
            res = session.exec(
                select(Author).where(Author.name.op("SOUNDS LIKE")(name_like))
            ).first()
            print("Response: ", res)
            if res is None:
                return None, session
            return res.jsonserialize(), session

    # def get_papers_written_by(self, author_id=None, author_name=None):
    #     with Connection().session() as session:
    #         statement = ""
    #         if author_name is None:
    #             statement = (
    #                 select(Publication, PublicationAuthorLink, Author)
    #                 .join(
    #                     PublicationAuthorLink,
    #                     PublicationAuthorLink.publication_id == Publication.result_id,
    #                 )
    #                 .join(Author, Author.author_id == PublicationAuthorLink.author_id)
    #                 .where(Author.author_id == author_id)
    #             )
    #         else:
    #             statement = (
    #                 select(Publication, PublicationAuthorLink, Author)
    #                 .join(
    #                     PublicationAuthorLink,
    #                     PublicationAuthorLink.publication_id == Publication.result_id,
    #                 )
    #                 .join(Author, Author.author_id == PublicationAuthorLink.author_id)
    #                 .where(Author.name == author_name)
    #             )

    #         res = session.exec(statement).all()
    #         print(f"print models!! {res}")
    #         arr: List = []
    #         brr: dict = {}
    #         for m in res:
    #             pub_id = m[1].publication_id
    #             brr[pub_id] = {"paper": [], "author": [], "publication_author_link": []}
    #         for m in res:
    #             arr.append({"publication": m[0], "author": m[1], "publication_author_link": m[2]})
    #             pub_id = m[1].publication_id
    #             brr[pub_id]["paper"] = m[0].jsonserialize()
    #             brr[pub_id]["author"].append(m[2].jsonserialize())
    #             brr[pub_id]["publication_author_link"].append(m[1].jsonserialize())
    #         crr = []
    #         for k in brr:
    #             crr.append(brr[k])
    #         return brr, session
    def get_papers_written_by(self, author_id=None, author_name=None):
        with Connection().session() as session:
            if author_name is None:
                statement = (
                    select(Publication, PublicationAuthorLink, Author)
                    .join(
                        PublicationAuthorLink,
                        PublicationAuthorLink.publication_id == Publication.result_id,
                    )
                    .join(Author, Author.author_id == PublicationAuthorLink.author_id)
                    .where(Author.author_id == author_id)
                )
            else:
                statement = (
                    select(Publication, PublicationAuthorLink, Author)
                    .join(
                        PublicationAuthorLink,
                        PublicationAuthorLink.publication_id == Publication.result_id,
                    )
                    .join(Author, Author.author_id == PublicationAuthorLink.author_id)
                    .where(Author.name == author_name)
                )

            res = session.exec(statement).all()

            papers_dict = {}
            for publication, pub_author_link, author in res:
                pub_id = pub_author_link.publication_id
                if not pub_id in papers_dict:
                    # Fetch all authors for the current publication
                    all_authors_statement = (
                        select(Author)
                        .join(
                            PublicationAuthorLink,
                            PublicationAuthorLink.author_id == Author.author_id,
                        )
                        .where(PublicationAuthorLink.publication_id == pub_id)
                    )
                    all_authors = session.exec(all_authors_statement).all()

                    papers_dict[pub_id] = {
                        "paper": publication.dict(),
                        "authors": [author.dict() for author in all_authors],
                    }

            papers_list = [
                {"paper": details["paper"], "authors": details["authors"]}
                for details in papers_dict.values()
            ]
            return papers_list, session

    def get_all_authors(self):
        with Connection().session() as session:
            statement = select(Author)
            res = session.exec(statement).all()
            arr = []
            for auth in res:
                arr.append(auth.jsonserialize())

            return arr, session

    def get_author_by_name(self, query):
        with Connection().session() as session:
            # Use ilike for case-insensitive search
            statement = select(Author).where(
                or_(Author.name.ilike(f"%{query}%"), Author.author_id.ilike(f"%{query}%"))
            )
            res = session.exec(statement).all()
            arr = [auth.jsonserialize() for auth in res]

            return arr, session

    def get_paper_by_name(self, name):
        query = name
        with Connection().session() as session:
            # Use ilike for case-insensitive search
            statement = select(Publication).where(
                or_(
                    Publication.title.ilike(f"%{query}%"), Publication.result_id.ilike(f"%{query}%")
                )
            )
            res = session.exec(statement).all()
            arr = [auth.jsonserialize() for auth in res]
            return arr, session

    def get_first_paper_by_name(self, name):
        query = name
        with Connection().session() as session:
            # Use ilike for case-insensitive search
            statement = select(Publication).where(
                or_(
                    Publication.title.ilike(f"%{query}%"), Publication.result_id.ilike(f"%{query}%")
                )
            )
            res = session.exec(statement).first()
            if res is not None:
                return res.jsonserialize(), session
            return None, session

    def search_publications(self, query_text):
        with Connection().session() as session:
            old_query_text = query_text
            query_text = to_sql_match(query_text)
            # Construct the SQL queries
            sql_query = """
                    SELECT p.result_id, p.title, p.snippet,
                        MATCH(p.title) AGAINST (:query_text IN BOOLEAN MODE) AS relevance,
                        GROUP_CONCAT(a.name SEPARATOR ', ') AS authors
                    FROM publication p
                    LEFT JOIN publicationauthorlink pal ON p.result_id = pal.publication_id
                    LEFT JOIN author a ON pal.author_id = a.author_id
                    WHERE MATCH(p.title) AGAINST (:query_text IN BOOLEAN MODE)
                    GROUP BY p.result_id
                    ORDER BY relevance DESC
            """
            sql_query_2 = """
                SELECT p.result_id, p.title, p.snippet,
                    MATCH(p.title) AGAINST (:query_text IN NATURAL LANGUAGE MODE) AS relevance,
                    GROUP_CONCAT(a.name SEPARATOR ', ') AS authors
                FROM publication p
                LEFT JOIN publicationauthorlink pal ON p.result_id = pal.publication_id
                LEFT JOIN author a ON pal.author_id = a.author_id
                WHERE p.title LIKE :like_query_text
                OR p.snippet LIKE :like_query_text
                GROUP BY p.result_id
                UNION ALL
                SELECT p.result_id, p.title, p.snippet,
                    MATCH(p.snippet) AGAINST (:query_text IN NATURAL LANGUAGE MODE) AS relevance,
                    GROUP_CONCAT(a.name SEPARATOR ', ') AS authors
                FROM publication p
                LEFT JOIN publicationauthorlink pal ON p.result_id = pal.publication_id
                LEFT JOIN author a ON pal.author_id = a.author_id
                WHERE p.title LIKE :like_query_text
                OR p.snippet LIKE :like_query_text
                GROUP BY p.result_id
                UNION ALL
                SELECT p.result_id, p.title, p.snippet,
                    (MATCH(p.title) AGAINST (:query_text IN BOOLEAN MODE) * 1) AS relevance,
                    GROUP_CONCAT(a.name SEPARATOR ', ') AS authors
                FROM publication p
                LEFT JOIN publicationauthorlink pal ON p.result_id = pal.publication_id
                LEFT JOIN author a ON pal.author_id = a.author_id
                WHERE MATCH(p.title) AGAINST (:query_text IN BOOLEAN MODE)
                GROUP BY p.result_id
                UNION ALL
                SELECT p.result_id, p.title, p.snippet,
                    MATCH(p.snippet) AGAINST (:query_text IN BOOLEAN MODE) AS relevance,
                    GROUP_CONCAT(a.name SEPARATOR ', ') AS authors
                FROM publication p
                LEFT JOIN publicationauthorlink pal ON p.result_id = pal.publication_id
                LEFT JOIN author a ON pal.author_id = a.author_id
                WHERE MATCH(p.snippet) AGAINST (:query_text IN BOOLEAN MODE)
                GROUP BY p.result_id
                ORDER BY relevance DESC
            """

            # Execute the SQL query and get mappings
            mappings = (
                session.execute(
                    text(sql_query),
                    {"query_text": query_text, "like_query_text": f"%{query_text}%"},
                )
                .mappings()
                .all()
            )

            print(f"\n\n GOT {len(mappings)} RESULTS FROM MAP1\n\n")

            mappings2 = (
                session.execute(
                    text(sql_query_2),
                    {"query_text": old_query_text, "like_query_text": f"%{old_query_text}%"},
                )
                .mappings()
                .all()
            )

            # print("\n-------QQ-------\n")
            # print(results)
            # print("\n----------------\n\n")
            results = [dict(row) for row in mappings]
            results2 = [dict(row) for row in mappings2]
            results = results + results2
            return results, session

    # def get_paper_by_name(self, name):
    #     with Connection().session() as session:
    #         statement = select(Publication).where(Publication.title == name)
    #         res = session.exec(statement).first()
    #         if res is None:
    #             return None, session

    #         return res.jsonserialize(), session

    def get_authors_of_paper(self, paper_id):
        with Connection().session() as session:
            statement = ""

            statement = (
                select(Publication, PublicationAuthorLink, Author)
                .join(
                    PublicationAuthorLink,
                    PublicationAuthorLink.publication_id == Publication.result_id,
                )
                .join(Author, Author.author_id == PublicationAuthorLink.author_id)
                .where(Publication.result_id == paper_id)
            )
            res = session.exec(statement).all()
            print(f"print models!! {res}")
            arr: List = []
            brr: dict = {}
            for m in res:
                pub_id = m[1].publication_id
                brr[pub_id] = {"paper": [], "author": [], "publication_author_link": []}
            for m in res:
                arr.append({"publication": m[0], "author": m[1], "publication_author_link": m[2]})
                pub_id = m[1].publication_id
                brr[pub_id]["paper"] = m[0].jsonserialize()
                brr[pub_id]["author"].append(m[2].jsonserialize())
                brr[pub_id]["publication_author_link"].append(m[1].jsonserialize())
            crr = []
            for k in brr:
                crr.append(brr[k])
            return brr, session

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

    def get_complete_papers_by_author(self, author_id=None, author_name=None):
        with Connection().session() as session:
            statement = ""
            # if author_name is not None:
            #     statement = select(
            #         Publication
            #     ).join(PublicationAuthorLink, PublicationAuthorLink.publication_id == Publication.result_id)\
            #         .join(Author, Author.author_id == PublicationAuthorLink.author_id) \
            #         .group_by(Publication.result_id)
            # else:
            #     statement = select(
            #         Publication
            #     ).join(PublicationAuthorLink, PublicationAuthorLink.author_id == Publication.result_id) \
            #         .join(Author, Author.author_id == PublicationAuthorLink.author_id) \
            #         .group_by(Publication.result_id)

            statement = (
                select(Publication, PublicationAuthorLink, Author)
                .join(
                    PublicationAuthorLink,
                    PublicationAuthorLink.publication_id == Publication.result_id,
                )
                .join(Author, Author.author_id == PublicationAuthorLink.author_id)
            )
            print("STATEMENT:", statement)
            res = session.exec(statement).all()
            print(f"print models!! {res}")
            arr: List = []
            brr: dict = {}
            for m in res:
                pub_id = m[1].publication_id
                brr[pub_id] = {"paper": [], "author": [], "publication_author_link": []}
            for m in res:
                arr.append({"publication": m[0], "author": m[1], "publication_author_link": m[2]})
                pub_id = m[1].publication_id
                brr[pub_id]["paper"] = m[0].jsonserialize()
                brr[pub_id]["author"].append(m[2].jsonserialize())
                brr[pub_id]["publication_author_link"].append(m[1].jsonserialize())
            crr = []
            for k in brr:
                crr.append(brr[k])
            return brr, session

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

    def update_profile_pic(self, user_id, picture):
        """Insert User

        Args:
            user (User : UserModel): user object
        """
        with Connection().session() as session:
            statement = select(UserModel).where(UserModel.user_id == user_id)
            user = session.exec(statement).first()
            if user is not None:
                user.picture = picture
                session.add(user)
                session.commit()
                session.refresh(user)
            return user, session

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
