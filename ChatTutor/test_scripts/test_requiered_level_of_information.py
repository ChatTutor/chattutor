import sys
sys.path.insert(0, ".")

from nice_functions import pprint 
from core.tutor import Tutor
from core.extensions import db
from core.openai_tools import load_api_keys

load_api_keys()
tutor = Tutor(db)

questions = [
    "list papers from 2020",
    "which papers study quantum information",
    "what is quantum information?"
]

for question in questions:
    r = tutor.get_requiered_level_of_information(question)
    pprint(r, question)