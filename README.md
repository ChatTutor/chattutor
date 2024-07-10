<img width="329" alt="image" src="https://github.com/ChatTutor/chattutor/assets/46609341/fe9dec71-8ac1-4c01-8657-07d0ffa584ff">


# ChatTutor
![Code Size](https://img.shields.io/github/languages/code-size/ChatTutor/chattutor)
![Repo Size](https://img.shields.io/github/repo-size/ChatTutor/chattutor)

[ChatTutor](https://dkeathley.github.io/6.2410-lab/intro.html) is an AI-agent capable of teaching and research communications, ranging from new learners to industry professionals, undergraduates, and graduate students. We aim for ChatTutor to possess deep domain-specific, hierarchical, and trust-weighted knowledge. 

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
If you would like an OpenAI API key for the purposes of developing our repository, please reach out to hkemeny@g.harvard.edu

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
   ./run.sh
```

3. **Interact with ChatTutor:**
Open a web browser and navigate to http://localhost:5000/ to interact with the application. Use the provided interface to ask questions and receive responses based on the loaded data sources.

## Components

1. core - contains the backend and the core code
  - blueprints - contains the APIs split into blueprints based on their purpose
  - data - contains the SQL database models
  - natlang & scripts & test_scripts - scripts for testing / modifying language
  - static - static files
  - tutor - variants of tutors used for different purposes

2. frontend - contains the angular frontend
  /src/app - frontend components

## Contribution Guidelines

If you'd like to contribute to ChatTutor, please take a look at our
[contribution guidelines](CONTRIBUTING.md). We use [GitHub issues](https://github.com/ChatTutor/chattutor/issues) for tracking requests and bugs. 
 
## Acknowledgements
![MIT](https://img.shields.io/badge/RLE-MIT-violet)
 
ChatTutor V1 was developed by Dirk Englund for the Spring 6.2410 course "Quantum Systems Engineering" at MIT. It was further developed with Hank Stennes, Hyeongrak "Chuck" Choi, and Hunter Kemeny in the summer of 2023, and late in the summer they were joined by Aatmik Mallya, Adrian and Alexandru Ariton, and a growing team of developers organized by Hunter and a cohort of key developers.
