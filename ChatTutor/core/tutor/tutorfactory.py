from abc import ABC, ABCMeta, abstractmethod
from enum import Enum
from core.tutor.variants.focusedcoursetutor import FocusedCourseTutor
from core.tutor.variants.restrictedcoursetutor import RestrictedCourseTutor
from core.tutor.tutor import Tutor
from core.tutor.cqntutor import CQNTutor
from core.tutor.sqlquerytutor import SQLQueryTutor


class TutorType(Enum):
    COURSE = 1
    NSF = 2  # for now only CQN


class CourseTutorType(Enum):
    COURSE_RESTRICTED = 1
    COURSE_FOCUSED = 2


class NSFTutorType(Enum):
    NSF_CQN = 1
    NSF_DEFAULT = 2  # not available for now
    NSF_SQL = 3


class TutorTypes:
    """Tutor Types from string

    Returns:
        match id:
            case "COURSE_FOCUSED":
                return CourseTutorType.COURSE_FOCUSED
            case "COURSE_RESTRICTED":
                return CourseTutorType.COURSE_RESTRICTED
            case "NSF_CQN":
                return NSFTutorType.NSF_CQN
            case "NSF_DEFAULT":
                return NSFTutorType.NSF_DEFAULT
            case _:
                return CourseTutorType.COURSE_RESTRICTED
    """

    @staticmethod
    def from_string(type_id: str):
        """Returns type from string

        Args:
            type_id (str): type

        Returns:
            CourseTutorType | NSFTutorType: the type
        """
        match type_id:
            case "COURSE_FOCUSED":
                return CourseTutorType.COURSE_FOCUSED
            case "COURSE_RESTRICTED":
                return CourseTutorType.COURSE_RESTRICTED
            case "NSF_CQN":
                return NSFTutorType.NSF_SQL
            case "NSF_DEFAULT":
                return NSFTutorType.NSF_DEFAULT
            case _:
                return CourseTutorType.COURSE_RESTRICTED


class TutorFactory:
    """Generates tutors based on type, and collections"""

    def __init__(self, embedding_db):
        self.db = embedding_db

    def build_course_tutor(
        self, tutor_subtype: CourseTutorType, focus_multiplier: None | int = None
    ) -> Tutor:
        chattutor: Tutor = None
        match tutor_subtype:
            case CourseTutorType.COURSE_RESTRICTED:
                chattutor = RestrictedCourseTutor(self.db, "-- RANDOM DB NAME --")
            case CourseTutorType.COURSE_FOCUSED:
                chattutor = FocusedCourseTutor(
                    self.db, "-- RANDOM DB NAME --", focus_multiplier=focus_multiplier
                )
            case _:
                # exception here!
                pass
        return chattutor

    def build_nsf_tutor(self, tutor_subtype: NSFTutorType) -> Tutor:
        chattutor: Tutor = None
        match tutor_subtype:
            case NSFTutorType.NSF_CQN:
                chattutor = CQNTutor(self.db, "-- RANDOM DB NAME --")
            case NSFTutorType.NSF_SQL:
                chattutor = SQLQueryTutor(self.db, gemini=False)
            case _:
                # exception here!
                pass
        return chattutor

    def build_empty(
        self, tutor_subtype: CourseTutorType | NSFTutorType, focus_multiplier=1.5
    ) -> Tutor:
        chattutor: Tutor = None
        if isinstance(tutor_subtype, CourseTutorType):
            chattutor = self.build_course_tutor(tutor_subtype, focus_multiplier=focus_multiplier)
        if isinstance(tutor_subtype, NSFTutorType):
            chattutor = self.build_nsf_tutor(tutor_subtype)
        return chattutor

    def build_(
        self,
        collection_names,
        collection_desc: None | str,
        multiple: None | bool,
        tutor_subtype: CourseTutorType | NSFTutorType,
    ) -> Tutor:
        chattutor: Tutor = self.build_empty(tutor_subtype=tutor_subtype)

        if multiple == None or multiple == False:
            name = collection_desc if collection_desc else ""
            chattutor.add_collection(collection_names, name)
        else:
            for cname in collection_names:
                message = (
                    f"CQN papers "
                    if cname == "test_embedding"
                    else """Use the following user uploaded files to provide information if asked about content from them. 
                User uploaded files """
                )
                chattutor.add_collection(cname, message)
        return chattutor

    def build(
        self,
        tutor_subtype: CourseTutorType | NSFTutorType,
        collection_names,
        collection_desc: None | str = None,
    ) -> Tutor:
        if isinstance(collection_names, (list, tuple)):
            return self.build_(collection_names, collection_desc, True, tutor_subtype)
        return self.build_(collection_names, collection_desc, False, tutor_subtype)
