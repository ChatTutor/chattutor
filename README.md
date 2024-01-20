# ChatTutor

ChatTutor is an AI kernel currently being trained on data from quantum related papers at the Center for Quantum Networks. It aims to provide students with information about scientists, citations and scientific discoveries or improvements. 

## Overview
This project is the web application for ChatTutor.

- production (main branch) hosted at [https://chattutor-git-nbqjgewnea-uc.a.run.app](https://chattutor-git-nbqjgewnea-uc.a.run.app)
- testing (beta-main branch) hosted at [https://beta-chattutor-nbqjgewnea-uc.a.run.app/](https://beta-chattutor-nbqjgewnea-uc.a.run.app/)

## Usage

1. Navigate to the **ChatTutor** folder and insert the **.env.yaml** file which should
have the following format:

```yaml
env_variables:
    CHATUTOR_GCP: TRUE
    OPENAI_API_KEY: <>
    ACTIVELOOP_TOKEN: <>
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
```sh
docker build -t chattutor .
docker run -p 5000:5000 chattutor
```

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
 
