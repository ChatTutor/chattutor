import os
import openai
import google.generativeai as genai

OPENAI_DEFAULT_MODEL = "gpt-4-1106-preview"


def load_api_keys():
    if "CHATTUTOR_GCP" in os.environ or "_CHATUTOR_GCP" in os.environ:
        openai.api_key = os.environ["OPENAI_API_KEY"]
        GOOGLE_API_KEY = os.environ["GEMINI_API_KEY"]
        genai.configure(api_key=GOOGLE_API_KEY)

    else:
        import yaml

        with open(".env.yaml") as f:
            yamlenv = yaml.safe_load(f)
        keys = yamlenv["env_variables"]
        os.environ["OPENAI_API_KEY"] = keys["OPENAI_API_KEY"]
        openai.api_key = keys["OPENAI_API_KEY"]
        GOOGLE_API_KEY = keys["GEMINI_API_KEY"]
        genai.configure(api_key=GOOGLE_API_KEY)
        os.environ["ACTIVELOOP_TOKEN"] = keys["ACTIVELOOP_TOKEN"]


def load_env():
    if "CHATTUTOR_GCP" in os.environ or "_CHATUTOR_GCP" in os.environ:
        pass
    else:
        import yaml

        with open(".env.yaml") as f:
            yamlenv = yaml.safe_load(f)
        keys = yamlenv["env_variables"]

        print(keys)

        envars = [
            "VECTOR_DB_HOST",
            "SQL_DB_HOST",
            "SQL_DB_USER",
            "SQL_DB_PASSWORD",
            "SQL_DB",
            "STAT_SQL_DB",
            "ROOT_USER",
            "ROOT_PW",
            "TRIGGER_ID",
            "OAUTH_CLIENT_ID",
            "OAUTH_CLIENT_SECRET",
            "PLATFORM",
            "SERVICE_NAME",
            "VERITAI_EMAIL",
            "VERITAI_EMAIL_PASSWD",
            "SERVICE_BASE_URL",
            "SERP_API_KEY",
            "GEMINI_API_KEY",
        ]

        for envar in envars:
            if envar in keys:
                print(envar)
                os.environ[envar] = keys[envar]
