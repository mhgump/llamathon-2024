from src.llama.base_prompts import LLamathonQueryBuilder


SYSTEM_PROMPT = """Act as an expert code analyst.
Answer questions about the supplied code.

Always reply to the user in the same language they are using."""

TEMPLATE = """Help me apply changes to appropriate files.

Read the following commit title, description, and diff.

```{diff}```

{instruction_1}

{instruction_2}

Follow these guidelines:
{guidelines}"""

INSTRUCTION_1 = """
This diff was applied when upgrading a python version. Help me identify snippets of the code
that are relevant to the version upgrade. This could include things like relevant dependencies and changing function names. Unchanged lines in the diff is unlikely to be relevant. Even in a changed line, unchanged text is still unlikely to be relevant. 
""".replace("\n", " ").strip()

INSTRUCTION_2 = """
Remove details that are only related to the specifics of this project and not related to the version upgrade.
I will use the snippets to perform a regex search.
""".replace("\n", " ").strip()

GUIDELINES = [
    "Respond as a numbered list. Each item should be enclosed in back quotes ``.",
    "Do not include snippets that do not appear in the above code.",
    "Do not include any explanations or text outside of the numbered list.",
    "Each snippet you suggest should appear exactly as is in the above code.",
]

EXAMPLE_DIFF_1 = """
@@ -20,11 +20,11 @@
 if sys.version_info >= (3, 9):
     DType_ref = types.GenericAlias(np.dtype, (ScalarType,))
     NDArray_ref = types.GenericAlias(np.ndarray, (Any, DType_ref))
-    FuncType = Callable[[Union[_GenericAlias, types.GenericAlias]], Any]
+    FuncType = Callable[["_GenericAlias | types.GenericAlias"], Any]
 else:
     DType_ref = Any
     NDArray_ref = Any
     # This code is only relevant for dependency sylvie. 
-    FuncType = Callable[[_GenericAlias], Any]
+    FuncType = Callable[["_GenericAlias"], Any]
 
 GETATTR_NAMES = sorted(set(dir(np.ndarray)) - _GenericAlias._ATTR_EXCEPTIONS)
 """

EXAMPLE_RESPONSE_1 = """Here is the list of snippets that you can use to identify files where the above fix needs to be applied:

``1. sys.version_info >= (3, 9)``
``2. FuncType = Callable[["_GenericAlias | types.GenericAlias"], Any]``
``3. FuncType = Callable[["_GenericAlias"], Any]``
"""

EXAMPLE_FEEDBACK_1 = """I will provide my feedback to the above suggestions. Afterwards, update your suggestions to the corrected final response.

``1. sys.version_info >= (3, 9)``
This is a bad solution as it is not relevant to the upgrade and it occurs in an unchanged line. 

``2. FuncType = Callable[["_GenericAlias | types.GenericAlias"], Any]``
This is a bad solution as it includes project specific changes such as Callable, Any, and the or | operator. Instead we should suggest _GenericAlias and types.GenericAlias separately. 

``3. FuncType = Callable[["_GenericAlias"], Any]``
This is a bad solution as it includes project specific changes such as Callable, Any, and the or | operator. Instead we should suggest just _GenericAlias.

Additionally, you left out an important suggestion for dependency sylvie. As mentioned, we are interested in suggesting things related to dependencies. 
"""

EXAMPLE_FINAL_RESPONSE_1 = """Thank you for the feedback! Based on your input, I will update my suggestions:

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
        .add_assistant_prompt(EXAMPLE_RESPONSE_1)\
        .add_user_prompt(EXAMPLE_FEEDBACK_1)\
        .add_assistant_prompt(EXAMPLE_FINAL_RESPONSE_1)\
        .add_user_prompt(TEMPLATE.format(
            diff=diff,
            instruction_1=INSTRUCTION_1,
            instruction_2=INSTRUCTION_2,
            guidelines="\n".join(GUIDELINES
        ))).query
