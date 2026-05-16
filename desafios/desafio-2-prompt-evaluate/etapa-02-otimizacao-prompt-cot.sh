#!/usr/bin/env bash
#
# Etapa 2 — Otimização do Prompt (Chain of Thought + Few-shot)
#
# Objetivo:
#   - Partir de prompts/bug_to_user_story_v1.yml (análise manual ou pull)
#   - Manter prompts/bug_to_user_story_v2.yml com persona, CoT, exemplos few-shot,
#     regras de formato Markdown / User Story e edge cases
#   - Validar com pytest tests/test_prompts.py
#
# Artefato principal: prompts/bug_to_user_story_v2.yml
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

echo ">>> Etapa 2: validação do prompt otimizado (tests/test_prompts.py)"
"$VENV_PY" -m pytest tests/test_prompts.py -v --tb=short
