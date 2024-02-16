from core.tutor.systemmsg import default_system_message
from core.openai_tools import OPENAI_DEFAULT_MODEL
from core.tutor.coursetutor import CourseTutor
from abc import ABC, ABCMeta, abstractmethod
from enum import Enum
from nice_functions import (pprint, bold, green, blue, red, time_it)

class FocusedCourseTutor(CourseTutor):
    def __init__(self, embedding_db, embedding_db_name: str, focus_multiplier : int = 1.5, system_message: str = default_system_message, engineer_prompts: bool = True):
        super().__init__(embedding_db, embedding_db_name, system_message, engineer_prompts)
        self.focus_multiplier = focus_multiplier
    
    def get_collection_valid_docs(self, prompt, coll_name, coll_desc, from_doc=None, 
                        threshold=0.5, query_limit=3):
        arr = []
        pprint("\nQuerying embedding_db with prompt:", blue(prompt))
        (
            documents,
            metadatas,
            distances,
            documents_plain,
        ) = time_it(self.embedding_db.query)(prompt, query_limit, from_doc=None, metadatas=True)
        
        (
            restricted_documents,
            restricted_metadatas,
            restricted_distances,
            restricted_documents_plain,
        ) = time_it(self.embedding_db.query)(prompt, query_limit, from_doc, metadatas=True)
        
        pprint(green(rf"got {len(documents)} general documents"))
        
        pprint(green(rf"got {len(restricted_documents)} restricted documents"))

        # add restricted documents regardless of distance, and multiply them!
        for doc, meta, dist in zip(restricted_documents, restricted_metadatas, restricted_distances):
            # if no fromdoc specified, and distance is lowe thhan thersh, add to array of possible related documents
            # if from_doc is specified, threshold is redundant as we have only one possible doc
            if dist <= threshold or from_doc != None:
                arr.append(
                    {
                        "coll_desc": coll_desc,
                        "coll_name": coll_name,
                        "doc": doc,
                        "metadata": meta,
                        "distance": dist / self.focus_multiplier,
                    }
                )
        # also add the other with normal distance 
        for doc, meta, dist in zip(documents, metadatas, distances):
            # if dist <= threshold:
            arr.append(
                {
                    "coll_desc": coll_desc,
                    "coll_name": coll_name,
                    "doc": doc,
                    "metadata": meta,
                    "distance": dist,
                }
            )
        return arr