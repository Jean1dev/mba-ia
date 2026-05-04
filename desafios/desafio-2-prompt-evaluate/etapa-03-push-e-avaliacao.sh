#!/usr/bin/env bash
#
# Etapa 3 — Push e Avaliação
#
# Objetivo:
#   - Enviar prompts/bug_to_user_story_v2.yml ao LangSmith Prompt Hub como
#     {USERNAME_LANGSMITH_HUB}/bug_to_user_story_v2 (público, com metadados)
#   - Executar src/evaluate.py contra o dataset e as métricas do projeto
#
# Variáveis .env: LANGSMITH_API_KEY, USERNAME_LANGSMITH_HUB, LLM_PROVIDER,
#   OPENAI_API_KEY ou GOOGLE_API_KEY, LANGSMITH_PROJECT (opcional), modelos.
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

echo ">>> Etapa 3a: push do prompt v2 para o LangSmith Hub"
"$VENV_PY" src/push_prompts.py

echo ""
echo ">>> Etapa 3b: avaliação (evaluate.py)"
"$VENV_PY" src/evaluate.py
