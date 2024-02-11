import pickle
import utils.questions as questions
import re
from utils.serialize import serialize_iteratively
from typing import Dict

import pathlib
from os.path import join

config_data_folder = join(pathlib.Path(__file__).parent.resolve(), "config_data")


def load(file_name: str, ask: bool=True, default=None, format: str = "pickle") -> Dict:
    import os
    import json

    loaded_dict = default

    if format == "json":
        file_name = os.path.join(f"{config_data_folder}", f"{file_name}.json")
        if os.path.isfile(file_name):
            try:
                with open(file_name, "r") as read_content:
                    loaded_dict = json.load(read_content)
            except:
                pass
        return loaded_dict

    elif format == "pickle":
        file_name = os.path.join(f"{config_data_folder}", f"{file_name}.bin")
        if os.path.isfile(file_name):
            try:
                with open(file_name, "rb") as pickle_file:
                    loaded_dict = pickle.load(pickle_file)
            except Exception as e:
                print("\n----------------------------------------------------")
                print(
                    f"While loading pickle data on {file_name}, an exception occurred:"
                )
                print(str(e))
                print("returning default value")
                print("----------------------------------------------------")
                return default

        if loaded_dict and (
            ask == False or questions.yes_no_question("\nLoad last config?")
        ):
            if "_toList" in loaded_dict:
                loaded_dict = loaded_dict["_toList"]
            return loaded_dict
        else:
            return default


def save(file_name: str, dict_to_save: Dict, format: str="pickle") -> None:
    import os

    if file_name == "":
        return
    if not os.path.exists(config_data_folder):
        os.mkdir(config_data_folder)

    if format == "json":
        import json

        dict_to_save = serialize_iteratively(dict_to_save)
        out_file = open(f"{config_data_folder}/{file_name}.json", "w")
        json.dump(dict_to_save, out_file, indent=4)
        out_file.close()

    elif format == "pickle":
        if isinstance(dict_to_save, (list, tuple, set)):
            dict_to_save = {"_toList": list(dict_to_save)}

        if isinstance(dict_to_save, dict):
            dict_to_save.pop("file_name", None)
            to_pickle = dict_to_save.copy()

            # remove elements we dont want to store
            for key, item in dict_to_save.items():
                if isinstance(item, (str, dict, int, float, list, re.Pattern)):
                    pass
                else:
                    to_pickle.pop(key, None)
        elif isinstance(dict_to_save, (int, str, float)):
            to_pickle = dict_to_save

        with open(f"{config_data_folder}/{file_name}.bin", "wb") as pickle_file:
            pickle.dump(to_pickle, pickle_file)
