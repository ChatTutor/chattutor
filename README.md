<img width="329" alt="image" src="https://github.com/ChatTutor/chattutor/assets/46609341/fe9dec71-8ac1-4c01-8657-07d0ffa584ff">


# ChatTutor
![Code Size](https://img.shields.io/github/languages/code-size/ChatTutor/chattutor)
![Repo Size](https://img.shields.io/github/repo-size/ChatTutor/chattutor)

[ChatTutor](https://barosandu.github.io/intro.html) is an AI-agent capable of teaching and research communications, ranging from new learners to industry professionals, undergraduates, and graduate students. We aim for ChatTutor to possess deep domain-specific, hierarchical, and trust-weighted knowledge. 

## Overview
![GitHub last commit](https://img.shields.io/github/last-commit/ChatTutor/chattutor)

- production (main branch) hosted at [chattutor.org](https://chattutor.org)
- testing (beta-main branch) hosted at [https://beta-chattutor-nbqjgewnea-uc.a.run.app](https://beta-chattutor-nbqjgewnea-uc.a.run.app)

## License
[![license](https://img.shields.io/badge/GitHub-GPL--3.0-informational)](https://www.gnu.org/licenses/gpl-3.0.en.html)

ChatTutor is an educational project. It is licensed under the GNU General Public License version 3.0 (GPL-3.0), which guarantees end users the freedom to run, study, share, and modify the software. 

See the LICENSE.txt file for more details.

## Configuration

First, clone this repository. Then navigate to the **ChatTutor** folder and create an **.env.yaml** file which should
have the following format:

```yaml
env_variables:
    CHATUTOR_GCP: false
    OPENAI_API_KEY: <your_openai_api_key>
```
If you would like an OpenAI API key for the purposes of developing our repository, please reach out to hkemeny@mit.edu

The project file tree should look like this:

```
root_folder (named chattutor)
|- ChatTutor/
      |- ... (other files and folders)
      |- .env.yaml (the file you added)
|- db/
      |- ...
|- README.md
|- requirements.txt
|- ...
```

## Usage

1. **Setup Virtual Environment and Install Dependencies**
```sh
   python -m venv .venv       # python3 -m venv .venv
   source .venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
```
Alternatively, use docker:
```docker build -t chattutor .;docker run -p 5000:5000 chattutor```

2. **Run the flask application**
```
   cd ChatTutor
   python main.py
```

3. **Interact with ChatTutor:**
Open a web browser and navigate to http://127.0.0.1:5000/ to interact with the application. Use the provided interface to ask questions and receive responses based on the loaded data sources.

## Components

### 1. **Flask Application**
   - **File**: `main.py`
     - Hosts a Flask application that serves **various** static files and handles **HTTP** routes.
     - The `ask` route **facilitates interaction** with the `tutor` module to **formulate** responses to user queries.
   - **File**: `extensions.py`
     - Defines **the configuration for the selected** database **service**.

### 2. **Tutor Module**
   - **File**: `tutor.py`
     - Contains **core** functions to **interface with** the OpenAI API.
     - **Crafts** responses based on user queries and **maintains** conversation context.

### 3. **Database Interaction**
   - **File**: `database.py`
     - Defines the `VectorDatabase` class **for managing vectorized data**.
     - **Facilitates** interaction with **various** database providers such as Chroma and Deeplake.
     - **Manages** the loading of data sources, **the addition of new texts**, and **execution of** queries.
   - **File**: `definitions.py`
     - Defines **fundamental** classes for **data structure and** parsing **of the** dataset.

### 4. **Text Reading and Parsing**
   - **File**: `loader.py`
     - **Execute** this file to **generate** embeddings for the dataset and **upload them to a cloud-based service**.
     - Utilizes `reader.py` to **systematically** parse each file in the dataset.
   - **File**: `reader.py`
     - Contains functions to read directories and parse files of **varied formats** (PDF, plaintext, Jupyter notebooks) into **discrete** text chunks.
     - **Employs** specialized parsing strategies for **each** file type.

### 5. **Frontend Components**
   - **File**: `index.js`
     - **Manages** user interactions on the client side.
     - **Orchestrates** the conversation flow, **transmits** user messages to the server, and **refreshes** the chat interface with responses.
   - **File**: `index.html`
     - Defines the **graphical user interface (GUI)** for the chatbot.

## Contribution Guidelines

If you'd like to contribute to ChatTutor, please take a look at our
[contribution guidelines](CONTRIBUTING.md). We use [GitHub issues](https://github.com/ChatTutor/chattutor/issues) for tracking requests and bugs. 
 
## Acknowledgements
![MIT](https://img.shields.io/badge/RLE-MIT-violet)
 
ChatTutor V1 was developed by Dirk Englund for the Spring 6.2410 course "Quantum Systems Engineering" at MIT. It was further developed with Hank Stennes, Hyeongrak "Chuck" Choi, and Hunter Kemeny in the summer of 2023, and late in the summer they were joined by Aatmik Mallya, Adrian and Alexandru Ariton, and a growing team of developers organized by Hunter and a cohort of key developers.
