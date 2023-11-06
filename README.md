# ChatTutor

Generative AI could mark the greatest change in education since the Enlightenment. A transformation will happen, one way or the other.  What is still undecided is is *how* this revolution will happen: will it be open, equitable, .. will it put science and openness first? Will it be open-access? Will these educational tools be based in free societies?  If we act now, we have a first-mover advantage to shape the future. 

The goal with Chattutor going forward is to develop an AI-agent capable of teaching and bringing together resaerch communictions, ranging from uninformed learners to industry professionals, undergraduates, and graduate students. The goal is for this AI-agent to possess deep domain-specific and hierarchical and trust-weighted knowledge. 

## Overview
This project is the web application for ChatTutor.

- production (main branch) hosted at [chattutor.org](https://chattutor.org)
- testing (beta-main branch) hosted at [https://beta-chattutor-nbqjgewnea-uc.a.run.app](https://beta-chattutor-nbqjgewnea-uc.a.run.app)

## Usage

1. Navigate to the **ChatTutor** folder and insert the **.env.yaml** file which should
have the following format:

```yaml
env_variables:
    CHATUTOR_GCP: TRUE
    OPENAI_API_KEY: <>
```

The project file tree should look like this:

```
root_folder (named chattutor)
|- ChatTutor/
      |- requirements.txt
      |- ... (other files and folders)
      |- .env.yaml (the file you added)
|- db/
      |- ...
|- README.md
```

2. **Setup Virtual Environment and Install Dependencies**
```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
```
Alternatively, use docker:
```docker build -t chattutor .;docker run -p 5000:5000 chattutor```

3. **Run the flask application**
```
   python main.py
```

4. **Interact with ChatTutor:**
Open a web browser and navigate to http://127.0.0.1:5000/ to interact with the application. Use the provided interface to ask questions and receive responses based on the loaded data sources.

## Components

### 1. **Flask Application**
   - **File**: `main.py`
     - Hosts a Flask application that serves static files and handles routes.
     - The `ask` route interacts with the `tutor` module to respond to user queries.
   - **File**: `extensions.py`
     - Defines which database is used


### 2. **Tutor Module**
   - **File**: `tutor.py`
     - Contains functions to interact with the OpenAI API.
     - Generates responses based on user queries and conversation context.


### 3. **Database Interaction**
   - **File**: `database.py`
     - Defines the `VectorDatabase` class.
     - Responsible for interacting with different database providers like Chroma and Deeplake.
     - Handles loading of data sources, adding texts, and performing queries.
   -  **File**: `definitions.py`
     - Defines basic classes for parsing the dataset


### 4. **Text Reading and Parsing**
   - **File**: `loader.py`
     - Run this file to compute the embeddings for the dataset and send it to the cloud.
     - Utilizes `reader.py` to parse each file in the dataset.
   - **File**: `reader.py`
     - Contains functions to read folders and parse files of different types (PDF, plaintext, Jupyter notebooks) into text chunks.
     - Utilizes different parsing strategies for different file types.


### 5. **Frontend Components**
   - **File**: `index.js`
     - Handles user interactions on the client side.
     - Manages the conversation, sends user messages to the server, and updates the chat with responses.
 - **File**: `index.html`
     - Defines the interface for the chat bot.

## Configuration
- API keys for OpenAI and Deep Lake are loaded from keys.json.
- Ensure that this file is correctly populated with the necessary keys before running the application.

## For Jupyter Book Web Deployment

To install Chattutor in a jupyter book, cd into chattutor_setup directory containing chattutor.css	chattutor.html	chattutor.js	install.py into the root directory. Run  "python chattutor_setup/install.py" to put chattutor code into the files located by the script. 

## Acknowledgements
Chattutor V1 was developed by Dirk Englund for the Spring 6.2410 course "Quantum Systems Engineering" at MIT.  It was further developed with Hank Stennes, H. Chuck Choi, and Hunter Kemeny in the summer of 2023, and late in the summer they were joined by Aatmik Mallya, Adrian Alexandru Ariton, and a growing team of developers under guidance by Hunter with a cohort of key developers (see github commit).
