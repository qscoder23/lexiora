import os
from pathlib import Path

import yaml


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_config() -> dict:
    config_path = get_project_root() / "config" / "settings.yaml"

    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

        deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
        if deepseek_api_key:
            config["llm"]["api_key"] = deepseek_api_key

        dashscope_api_key = os.environ.get("DASHSCOPE_API_KEY")
        if dashscope_api_key:
            config["embedding"]["api_key"] = dashscope_api_key

        neo4j_password = os.environ.get("NEO4J_PASSWORD")
        if neo4j_password:
            config["neo4j"]["password"] = neo4j_password

        return config
