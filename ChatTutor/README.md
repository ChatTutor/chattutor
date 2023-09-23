# ChatTutor

## Overview
This project is the web application for ChatTutor.

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


## Usage

1. **Setup Virtual Environment and Install Dependencies**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt```

2. **Run the flask application**
   ```
   python main.py
   ```

3. **Interact with ChatTutor:**
Open a web browser and navigate to http://127.0.0.1:5000/ to interact with the application. Use the provided interface to ask questions and receive responses based on the loaded data sources.

## Configuration
- API keys for OpenAI and Deep Lake are loaded from keys.json.
- Ensure that this file is correctly populated with the necessary keys before running the application.
