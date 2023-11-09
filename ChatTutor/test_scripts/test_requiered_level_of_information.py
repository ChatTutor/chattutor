import sys
from time import sleep
sys.path.insert(0, ".")

from nice_functions import pprint 
from core.tutor import Tutor
from core.extensions import db
from core.openai_tools import load_api_keys

load_api_keys()
tutor = Tutor(db)

BASIC = "basic"
MEDIUM = "medium"
HIGH = "high"
DB_SUMMARY = "db_summary"

questions = [
    ("list all papers related to Condensed Matter Physics", MEDIUM),
    ("what is quantum information?",HIGH),
    ("What papers were published in the year 2020?", BASIC),
    ("which papers study quantum information",MEDIUM),
    ("Can you summarize the content of the database?", DB_SUMMARY),
    ("can you summarize the db?",DB_SUMMARY),
    ("Are there any similar papers to the one titled 'Entanglement-enhanced testing of multiple quantum hypotheses'?", MEDIUM),
    ("Which is the most recent paper by X?", BASIC),
    ("Is the paper ''Entanglement-enhanced testing of multiple quantum hypotheses' in the database?", BASIC),
    ("Is the paper 'the reality is comming' in the database?", BASIC),
    ("Can you summarize the paper titled 'Quantum Networking Protocols' for me?", HIGH),
    ("Can you list all papers present in the database?", BASIC),
    ("which more papers do you know?",BASIC),
    ("Can you find papers authored by X?", BASIC ),
    ("Which one is the most recent paper from by X?", BASIC ),
    ("list papers from 2020",BASIC),
    ("Can you recommend papers related to quantum entanglement?", MEDIUM),
]

for question, expected_answer in questions:
    r = tutor.get_requiered_level_of_information(question, explain = False)
    pprint(r,expected_answer, question)
    sleep(1)

    if r != expected_answer:
        # r = tutor.get_requiered_level_of_information2(question, explain = True)
        raise(Exception(rf"{question} return {r}, and {expected_answer} was expected!"))
    