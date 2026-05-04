"""
Testes automatizados para validação de prompts."""
import pytest
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_V2_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture
def prompt_v2():
    data = load_prompts(PROMPT_V2_PATH)
    return data["bug_to_user_story_v2"]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_v2):
        assert "system_prompt" in prompt_v2
        assert prompt_v2["system_prompt"].strip()

    def test_prompt_has_role_definition(self, prompt_v2):
        text = (
            prompt_v2["system_prompt"]
            + prompt_v2.get("user_prompt", "")
        ).lower()
        assert "product manager" in text or "você é um" in text

    def test_prompt_mentions_format(self, prompt_v2):
        text = prompt_v2["system_prompt"].lower()
        assert "markdown" in text or "como [" in text or "como um" in text or "critérios de aceitação" in text

    def test_prompt_has_few_shot_examples(self, prompt_v2):
        text = prompt_v2["system_prompt"].lower()
        assert (
            "exemplo 1" in text
            and "entrada" in text
            and ("saída" in text or "saída esperada" in text)
        )

    def test_prompt_no_todos(self, prompt_v2):
        combined = prompt_v2["system_prompt"] + str(prompt_v2.get("user_prompt", ""))
        assert "[TODO]" not in combined

    def test_minimum_techniques(self, prompt_v2):
        techniques = prompt_v2.get("techniques_applied", [])
        assert isinstance(techniques, list)
        assert len(techniques) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
