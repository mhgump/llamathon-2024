from typing import Dict, List


class LLamathonQueryBuilder:
    def __init__(self):
        self.query: List[Dict[str, str]] = []

    def add_system_prompt(self, prompt: str):
        self.query.append({"role": "system", "content": prompt})
        return self

    def add_user_prompt(self, prompt: str):
        self.query.append({"role": "user", "content": prompt})
        return self

    def add_assistant_prompt(self, prompt: str):
        self.query.append({"role": "assistant", "content": prompt})
        return self
