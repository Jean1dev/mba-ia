#!/usr/bin/env bash
#
# Etapa 1 — Pull do Prompt inicial do LangSmith
#
# Objetivo:
#   - Garantir LANGSMITH_API_KEY (e demais variáveis) no arquivo .env a partir de .env.example
#   - Executar o pull do prompt público leonanluppi/bug_to_user_story_v1 no LangSmith Prompt Hub
#   - Persistir o resultado em prompts/bug_to_user_story_v1.yml
#
# Pré-requisitos: Python 3.9+ com módulo venv (ex.: sudo apt install python3-venv), .env configurado
#

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

VENV_PY="$ROOT/venv/bin/python"

ensure_python_env() {
  if [[ ! -x "$VENV_PY" ]]; then
    echo ">>> Criando venv em $ROOT/venv ..."
    if ! python3 -m venv "$ROOT/venv"; then
      echo "❌ Falha ao criar venv. Em Debian/Ubuntu: sudo apt install python3-venv"
      exit 1
    fi
    VENV_PY="$ROOT/venv/bin/python"
  fi
  if ! "$VENV_PY" -c "import dotenv" 2>/dev/null; then
    echo ">>> Instalando dependências (requirements.txt) ..."
    "$ROOT/venv/bin/pip" install -r "$ROOT/requirements.txt"
  fi
}

ensure_python_env

echo ">>> Etapa 1: pull do prompt inicial (LangSmith Hub -> prompts/bug_to_user_story_v1.yml)"
"$VENV_PY" src/pull_prompts.py
