from typing import List, Tuple

from src.llama.base_prompts import LLamathonQueryBuilder


LAZY_PROMPT = """You are diligent and tireless!
You NEVER leave comments describing code without implementing it!
You always COMPLETELY IMPLEMENT the needed code!"""

SYSTEM_PROMPT = """Act as an expert software developer.
Always use best practices when coding.
Respect and use existing conventions, libraries, etc that are already present in the code base.
Always reply to the user in the same language they are using.

For each file that needs to be changed, write out the changes similar to a unified diff like `diff -U0` would produce."""

TEMPLATE_INTRO = """Help me apply a fix to my code.
I will provide an example of the fix that needs to be applied.
I will then provide snippets from the file that needs to be updated.
""".strip().split('\n')

DIFF_INTRO = """
Read the following commit title, description, and diff the reference commit.
This is an example of the fix that should be applied.
""".strip().split('\n')

TEMPLATE_OUTRO = """Your task is to generate a change that applies the fix to the files.
Follow the same pattern as in the reference commits and apply it to the snippets provided.
Provide only the updated content of each Python snippet without any additional explanations.
""".strip().split('\n')

TEMPLATE = """{TEMPLATE_INTRO}

{DIFF_INTRO}

```{diff}```

Now read the follow snippets from the file that needs to be updated.

{snippets}

{TEMPLATE_OUTRO}"""


def get_prompt(diff: str, snippets: List[Tuple[str, str]]):
    formatted_snippets = "\n".join([f"{i+1}.{e[0]}\n```{e[1]}```" for i, e in enumerate(snippets)])
    return LLamathonQueryBuilder()\
        .add_system_prompt(SYSTEM_PROMPT)\
        .add_user_prompt(TEMPLATE.format(
            TEMPLATE_INTRO='\n'.join(TEMPLATE_INTRO),
            DIFF_INTRO='\n'.join(DIFF_INTRO),
            diff=diff,
            snippets=formatted_snippets,
            TEMPLATE_OUTRO='\n'.join(TEMPLATE_OUTRO)
        )).query
