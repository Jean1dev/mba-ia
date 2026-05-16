"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()

YAML_PATH = Path(__file__).resolve().parent.parent / "prompts" / "bug_to_user_story_v2.yml"
YAML_KEY = "bug_to_user_story_v2"


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    return validate_prompt_structure(prompt_data)


def _prompt_data_to_chat_template(prompt_data: dict) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", prompt_data["system_prompt"]),
            ("human", prompt_data["user_prompt"]),
        ]
    )


def _readme_content(prompt_data: dict) -> str:
    lines = [
        f"# {YAML_KEY}",
        "",
        prompt_data.get("description", "").strip(),
        "",
        f"**Versão:** {prompt_data.get('version', '')}",
        "",
        "**Técnicas aplicadas:** "
        + ", ".join(prompt_data.get("techniques_applied", []) or []),
        "",
    ]
    return "\n".join(lines).strip() + "\n"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    valid, errors = validate_prompt(prompt_data)
    if not valid:
        print("❌ Validação do prompt falhou:")
        for err in errors:
            print(f"   - {err}")
        return False

    try:
        tpl = _prompt_data_to_chat_template(prompt_data)
    except Exception as e:
        print(f"❌ Erro ao montar ChatPromptTemplate: {e}")
        return False

    description = (prompt_data.get("description") or "").strip()
    tags = list(prompt_data.get("tags") or [])
    techniques = prompt_data.get("techniques_applied") or []
    for t in techniques:
        tag = f"technique:{t}"
        if tag not in tags:
            tags.append(tag)

    client = Client()
    try:
        url = client.push_prompt(
            prompt_name,
            object=tpl,
            is_public=True,
            description=description or None,
            readme=_readme_content(prompt_data),
            tags=tags or None,
        )
        print(f"✓ Push concluído: {url}")
        return True
    except Exception as e:
        msg = str(e)
        print(f"❌ Falha no push para '{prompt_name}': {msg}")
        if "another tenant" in msg.lower() or "tenant" in msg.lower() and "cannot" in msg.lower():
            print(
                "\nO primeiro segmento do nome (antes de /) precisa ser o namespace do seu workspace "
                "LangSmith associado a esta LANGSMITH_API_KEY — não pode ser o usuário de outra conta.\n"
                "Ajuste USERNAME_LANGSMITH_HUB no .env para o handle do seu tenant (ex.: o indicado na "
                "mensagem de erro como \"Current tenant\", ou o nome que aparece em smith.langchain.com "
                "ao criar prompts no Hub)."
            )
        return False


def main():
    print_section_header("PUSH DE PROMPTS — LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    username = (os.getenv("USERNAME_LANGSMITH_HUB") or "").strip().strip("/")
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB vazio ou inválido.")
        return 1

    prompt_name = f"{username}/bug_to_user_story_v2"
    print(f"Destino: {prompt_name} (público)\n")

    data = load_yaml(str(YAML_PATH))
    if not data or YAML_KEY not in data:
        print(f"❌ Arquivo {YAML_PATH} sem a chave '{YAML_KEY}'.")
        return 1

    prompt_data = data[YAML_KEY]
    if push_prompt_to_langsmith(prompt_name, prompt_data):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
