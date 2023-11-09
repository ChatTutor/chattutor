import os
import openai

def load_api_keys():
    if "CHATTUTOR_GCP" in os.environ or "_CHATUTOR_GCP" in os.environ:
        openai.api_key = os.environ["OPENAI_API_KEY"]
    else:
        import yaml

        with open(".env.yaml") as f:
            yamlenv = yaml.safe_load(f)
        keys = yamlenv["env_variables"]
        os.environ["OPENAI_API_KEY"] = keys["OPENAI_API_KEY"]
        openai.api_key = keys["OPENAI_API_KEY"]