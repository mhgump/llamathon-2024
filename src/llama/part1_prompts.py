from src.llama.base_prompts import SYSTEM_PROMPT, LLamathonQueryBuilder


TEMPLATE = """Help me apply changes to appropriate files.

Read the following commit title, description, and diff.

```{diff}```

{instruction_1}

{instruction_2}

Follow these guidelines:
{guidelines}"""

INSTRUCTION_1 = """
I am searching through other files to find files that need the above fix to be applied.
Help me identify files where the above change is relevant.
To do this, identify snippets of the above code that would ONLY appear when the above change is applicable.
""".replace("\n", " ").strip()

INSTRUCTION_2 = """
In other words, look for snippets that are related to the fix being performed.
Remove details that are only related to the specifics above the project and not related to the fix.
I will use the snippets to perform a regex search.
""".replace("\n", " ").strip()

GUIDELINES = [
    "Respond as a numbered list. Each item should be enclosed in back quotes ``.",
    "Do not include snippets that do not appear in the above code.",
    "Do not include any explanations.",
    "Each snippet you suggest should appear exactly as is in the above code.",
]

EXAMPLE_DIFF_1 = """Subject: [PATCH] TST,TYP: Fix a python 3.11 failure for the `GenericAlias` tests

--- a/numpy/typing/tests/test_generic_alias.py
+++ b/numpy/typing/tests/test_generic_alias.py
@@ -20,11 +20,11 @@
 if sys.version_info >= (3, 9):
     DType_ref = types.GenericAlias(np.dtype, (ScalarType,))
     NDArray_ref = types.GenericAlias(np.ndarray, (Any, DType_ref))
-    FuncType = Callable[[Union[_GenericAlias, types.GenericAlias]], Any]
+    FuncType = Callable[["_GenericAlias | types.GenericAlias"], Any]
 else:
     DType_ref = Any
     NDArray_ref = Any
-    FuncType = Callable[[_GenericAlias], Any]
+    FuncType = Callable[["_GenericAlias"], Any]

 GETATTR_NAMES = sorted(set(dir(np.ndarray)) - _GenericAlias._ATTR_EXCEPTIONS)"""

EXAMPLE_RESPONSE = """Here is the list of snippets that you can use to identify files where the above fix needs to be applied:

1. `types.GenericAlias`
2. `Callable[[Union[_GenericAlias, types.GenericAlias]], Any]`
3. `_GenericAlias`
4. `_GenericAlias._ATTR_EXCEPTIONS`
5. `types.GenericAlias(np.dtype, (ScalarType,))`"""

EXAMPLE_FEEDBACK = """I will provide my feedback to the above suggestions. Afterwards, update your suggestions to the corrected final response.

1. `types.GenericAlias`
This is a correct suggestion.

2. `Callable[[Union[_GenericAlias, types.GenericAlias]], Any]`
This includes specifics of the project and is not directly related to the fix. For example the usage of `Callable` and `Union`

3. `_GenericAlias`
This is a correct suggestion.

4. `_GenericAlias._ATTR_EXCEPTIONS`
This does not appear in the changed lines so it is not likely to be relevant.

5. `types.GenericAlias(np.dtype, (ScalarType,))`
This does not appear in the changed lines so it is not likely to be relevant."""

EXAMPLE_FINAL_RESPONSE = """Thank you for the feedback! Based on your input, I will update my suggestions:

1. `types.GenericAlias`
2. `_GenericAlias`

These two snippets are directly related to the fix and can be used to identify files where the same fix needs to be applied.
"""


def get_prompt(diff: str):
    return LLamathonQueryBuilder()\
        .add_system_prompt(SYSTEM_PROMPT)\
        .add_user_prompt(TEMPLATE.format(
            diff=EXAMPLE_DIFF_1,
            instruction_1=INSTRUCTION_1,
            instruction_2=INSTRUCTION_2,
            guidelines="\n".join(GUIDELINES)))\
        .add_assistant_prompt(EXAMPLE_RESPONSE)\
        .add_user_prompt(EXAMPLE_FEEDBACK)\
        .add_assistant_prompt(EXAMPLE_FINAL_RESPONSE)\
        .add_user_prompt(TEMPLATE.format(
            diff=diff,
            instruction_1=INSTRUCTION_1,
            instruction_2=INSTRUCTION_2,
            guidelines="\n".join(GUIDELINES
        ))).query
