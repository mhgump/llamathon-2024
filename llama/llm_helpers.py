from enum import Enum
from groq import Groq
from typing import Dict, List


class LLamathonQueryBuilder:
    def __init__(self):
        self.query = []

    def add_system_prompt(self, prompt: str):
        self.query.append({"role": "system", "content": prompt})
        return self

    def add_user_prompt(self, prompt: str):
        self.query.append({"role": "user", "content": prompt})
        return self

    def add_assistant_prompt(self, prompt: str):
        self.query.append({"role": "assistant", "content": prompt})
        return self


class SupportedClients(Enum):
    GROQ = "groq"
    ANYSCALE = "anyscale"
    BASETEN = "baseten"


class SupportedModels(Enum):
    LLAMA31_70b = "llama31_70b"


class LLamathonClient:
    MODEL_ID_LOOKUP = {
        SupportedClients.GROQ.value: {
            SupportedModels.LLAMA31_70b.value: "llama-3.1-70b-versatile",
        }
    }

    def __init__(self):
        self._clients = {}
        self._model = SupportedModels.LLAMA31_70b
        self._default_client = None

    def load_groq_client(self):
        groq_api_key = open("GROQ_API_KEY", "r").read().strip()
        self._clients[SupportedClients.GROQ.value] = Groq(api_key=groq_api_key)
        if self._default_client is None:
            self._default_client = SupportedClients.GROQ.value

    def set_model(self, model: SupportedModels):
        self._model = model

    def set_default_client(self, client: SupportedClients):
        assert client in self._clients, f"Client {client} not loaded."
        self._default_client = client

    def get(self, query: List[Dict[str, str]]):
        assert self._default_client is not None, "No client available."
        self._validate_query(query, self._default_client)
        if self._default_client == SupportedClients.GROQ.value:
            return self._get_groq(query)

    @staticmethod
    def _validate_query(query: List[Dict[str, str]], client: SupportedClients):
        if client == SupportedClients.GROQ.value:
            for item in query:
                assert "role" in item, "Role not specified in query."
                assert item["role"] in ["system", "user", "assistant"], "Invalid role specified in query."
                assert "content" in item, "Content not specified in query."

    def _get_groq(self, query: List[Dict[str, str]], max_tokens=256):
        client = self._clients[SupportedClients.GROQ.value]
        completion = client.chat.completions.create(
            model=self.MODEL_ID_LOOKUP[SupportedClients.GROQ.value][self._model.value],
            messages=query,
            temperature=1,
            max_tokens=max_tokens,
            top_p=1,
            stream=False,
            stop=None,
        )
        return completion.choices[0].message
