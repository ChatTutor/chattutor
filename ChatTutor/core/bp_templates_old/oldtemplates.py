# import pymysql

import flask
from core.extensions import (db)
from core.tutor import (Tutor)
from flask import (Blueprint, Response, redirect, url_for)
from nice_functions import pprint, time_it

# import markdown


temp_bp = Blueprint("bp_templates_old", __name__)


@temp_bp.route("/cqn")
def cqn() -> str:
    """
    Serves the landing page of the web application which provides
    the ChatTutor interface. Users can ask the Tutor questions and it will
    response with information from its database of papers and information.
    Redirects the root URL to the index.html in the static folder
    """

    load_api_keys()
    tutor = Tutor(db)
    db.load_datasource("test_embedding_basic")
    print("getting number of documents...")
    docs = db.datasource.get(include=[])
    total_papers = len(docs["ids"])
    pprint("total_papers", total_papers)
    print("generating welcoming message...")

    welcoming_message = f"""
                <p>Welcome to the Center for Quantum Networks (CQN) website! I am your Interactive Research Assistant, here to assist you in exploring the wealth of knowledge within the CQN research database. With access to a vast collection of <b>{total_papers}</b> research papers, I am equipped to provide insightful and accurate responses to your queries.</p>
                <p>Whether you are looking for papers by a specific author, papers from a particular date or journal, or papers related to a specific topic or subject, I've got you covered. I can also help you find similar papers to ones you already know or even provide paper summaries.</p>
                <p>Here are some examples of questions you can ask:</p>
                <ul>
                    <li>Can you summarize the content of the database?</li>
                    <li>Can you list all papers present in the database?</li>
                    <li>Can you find papers authored by Dirk Englund?</li>
                    <li>What papers were published in the year 2020?</li>
                    <li>Which is the most recent paper by Dirk Englund?</li>
                    <li>Can you recommend papers related to quantum entanglement?</li>
                    <li>Are there any similar papers to the one titled 'Entanglement-enhanced testing of multiple quantum hypotheses'?</li>
                    <li>Can you summarize the paper titled 'Quantum Networking Protocols' for me?</li>
                </ul>
                <p>Feel free to explore the CQN research database and ask any questions you may have. I'm here to assist you on your research journey!</p>    
    """

    # welcoming_message = "" # disable to generate a new one using simple_gpt
    if welcoming_message == "":
        welcoming_message = time_it(tutor.simple_gpt)(
            f"""
        You are embedded into the Center for Quantum Networks (CQN) website as an Interactive Research Assistant. 
        Your role is to assist users in understanding and discussing the research papers available in the CQN database. 
        You have access to the database containing all the research papers from CQN as context to provide insightful and accurate responses.
        Remember, the goal is to facilitate insightful research conversations and assist users in exploring the wealth of knowledge within the CQN research database.
        The total number of papers you know is {total_papers}
        
        You can:
        - search papers by author, date, journal
        - search papers related to a topic or subject
        - find similar papers to others
        - summarize articles
        """,
            "Make an introductory message of yourself mentioning who you are, how many papers do you know, and what you can do to help users. Also, give examples of questions to related to what you can do. Do it in 200 words and generate the response in HTML",
            models_to_try=["gpt-3.5-turbo"],
        )

    return flask.render_template("cqn.html", welcoming_message=welcoming_message)


@temp_bp.route("/chattutor")
def chattutor() -> Response:
    """
    Serves the landing page of the web application which provides
    the ChatTutor interface. Users can ask the Tutor questions and it will
    response with information from its database of papers and information.
    Redirects the root URL to the index.html in the static folder
    """
    return redirect(url_for("static", filename="chattutor.html"))


@temp_bp.route("/interpreter")
def interpreter() -> Response:
    """
    Serves the landing page of the web application which provides
    the ChatTutor interface. Users can ask the Tutor questions and it will
    response with information from its database of papers and information.
    Redirects the root URL to the index.html in the static folder
    """
    return redirect(url_for("static", filename="interpreter.html"))
