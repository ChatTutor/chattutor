import os
import openai


# GPT Models
GPT_4_TURBO = "gpt-4-1106-preview"
GPT_4 = "gpt-4"
GPT_35_TURBO = "gpt-3.5-turbo-16k"
MODELS = [
    GPT_4_TURBO,
    GPT_4,
    GPT_35_TURBO
]

def get_default_model():
    return MODELS[0]

def get_models():
    return MODELS


def simple_gpt(system_message, user_message, selected_model=None, temperature=1):
    if not selected_model: selected_model = get_default_model()
    response = openai.ChatCompletion.create(
        model=selected_model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        # stream=True,
    )
    return response.choices[0].message.content

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
        os.environ["ACTIVELOOP_TOKEN"] = keys["ACTIVELOOP_TOKEN"]