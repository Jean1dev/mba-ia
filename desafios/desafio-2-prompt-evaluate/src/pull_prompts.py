"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import (
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables import RunnableBinding, RunnableSequence
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_HUB_NAME = "leonanluppi/bug_to_user_story_v1"
YAML_KEY = "bug_to_user_story_v1"


def _unwrap_chat_prompt_template(obj):
    seen = set()
    cur = obj
    while cur is not None and id(cur) not in seen:
        seen.add(id(cur))
        if isinstance(cur, ChatPromptTemplate):
            return cur
        if isinstance(cur, RunnableSequence):
            cur = cur.first
            continue
        if isinstance(cur, RunnableBinding):
            cur = cur.bound
            continue
        steps = getattr(cur, "steps", None)
        if steps:
            cur = steps[0]
            continue
        break
    return obj if isinstance(obj, ChatPromptTemplate) else None


def _message_template_text(msg) -> str:
    p = getattr(msg, "prompt", None)
    if p is not None:
        t = getattr(p, "template", None)
        if isinstance(t, str):
            return t
    return str(msg)


def _chat_prompt_to_record(prompt: ChatPromptTemplate, hub_name: str) -> dict:
    system_chunks = []
    human_chunks = []
    other_chunks = []

    for msg in prompt.messages:
        if isinstance(msg, SystemMessagePromptTemplate):
            system_chunks.append(_message_template_text(msg))
        elif isinstance(msg, HumanMessagePromptTemplate):
            human_chunks.append(_message_template_text(msg))
        elif isinstance(msg, AIMessagePromptTemplate):
            other_chunks.append(_message_template_text(msg))
        else:
            other_chunks.append(_message_template_text(msg))

    system_prompt = "\n\n".join(x.strip() for x in system_chunks if x.strip()).strip()
    user_prompt = "\n\n".join(x.strip() for x in human_chunks if x.strip()).strip()

    if other_chunks and not system_prompt:
        system_prompt = "\n\n".join(x.strip() for x in other_chunks if x.strip()).strip()
    elif other_chunks:
        system_prompt = (
            system_prompt
            + "\n\n"
            + "\n\n".join(x.strip() for x in other_chunks if x.strip()).strip()
        ).strip()

    if not user_prompt:
        user_prompt = "{bug_report}"

    return {
        YAML_KEY: {
            "description": f"Prompt puxado do LangSmith Hub ({hub_name})",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }


def pull_prompts_from_langsmith() -> bool:
    print_section_header("PULL DO LANGSMITH HUB")
    print(f"Prompt: {PROMPT_HUB_NAME}\n")

    try:
        pulled = hub.pull(PROMPT_HUB_NAME)
    except Exception as e:
        print(f"❌ Falha ao puxar o prompt: {e}")
        return False

    prompt_template = _unwrap_chat_prompt_template(pulled)
    if prompt_template is None:
        print(
            "❌ Não foi possível obter ChatPromptTemplate a partir do artefato do Hub."
        )
        return False

    record = _chat_prompt_to_record(prompt_template, PROMPT_HUB_NAME)
    out_path = Path(__file__).resolve().parent.parent / "prompts" / "bug_to_user_story_v1.yml"

    if not save_yaml(record, str(out_path)):
        return False

    print(f"✓ Salvo em: {out_path}")
    return True


def main():
    print_section_header("PULL DE PROMPTS — LANGSMITH")
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1
    if pull_prompts_from_langsmith():
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
