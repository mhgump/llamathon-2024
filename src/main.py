from collections import defaultdict
import json
import requests
import sys
from typing import List

from src.scripts.matching import match_snippet
from src.llama.generation_prompts import get_prompt
from src.llama import llm_helpers


COMMIT_DATA = "src/scripts/output/tagged_good_commits.json"


def find_commit_info(commit_sha):
    json_data = json.load(open(COMMIT_DATA, 'r'))
    for project_name in json_data:
        for commit_item in json_data[project_name]:
            if commit_item["sha"] == commit_sha:
                return project_name, commit_item["tags"]


def get_diff_contents(repo_full_name, commit_sha):
    uri = f'https://github.com/{repo_full_name}/commit/{commit_sha}.patch'
    return '\n'.join(requests.get(uri).content.decode().split('\n')[3:])


def process_codeblocks_list(codeblocks: List[int], max_linenumber: int):
    codeblocks = sorted(codeblocks)
    ranges = []
    for linenumber in codeblocks:
        ranges.append((max(0, linenumber - 5), min(linenumber + 5, max_linenumber)))
    merged_ranges = []
    for start, end in ranges:
        if not merged_ranges or start > merged_ranges[-1][1]:
            merged_ranges.append((start, end))
        else:
            merged_ranges[-1] = (merged_ranges[-1][0], end)
    augmented_ranges = []
    removed_lines = 0
    for i, (start, end) in enumerate(merged_ranges):
        starting_point = start - removed_lines
        augmented_ranges.append((start, end, starting_point))
        removed_lines += end - start
    return augmented_ranges


def main():
    working_directory = sys.argv[1]
    project_shortname = sys.argv[2]
    python_version = sys.argv[3]
    commit_sha = sys.argv[4]
    project_name, commit_info = find_commit_info(commit_sha)
    snippet, snippet_extension = commit_info[0]
    diff = get_diff_contents(project_name, commit_sha)
    matches = match_snippet(working_directory, project_shortname, python_version, snippet, snippet_extension)
    max_line_numbers = {}
    clean_filenames = {}
    codeblocks_map = defaultdict(list)
    for filename, clean_filename, linenumber in matches:
        clean_filenames[filename] = clean_filename
        with open(filename, 'r') as f:
            lines = f.readlines()
            max_line_numbers[filename] = len(lines)
        codeblocks_map[filename].append(linenumber)
    for filename in codeblocks_map:
        codeblocks_map[filename] = process_codeblocks_list(codeblocks_map[filename], max_line_numbers[filename])
    snippets = []
    filename_to_snippets = defaultdict(list)
    for filename, codeblocks in codeblocks_map.items():
        clean_filename = clean_filenames[filename]
        with open(filename, 'r') as f:
            lines = f.readlines()
        for start, end, starting_point in codeblocks:
            text = "\n".join(lines[start:end])
            snippets += [(f"{clean_filename}#L{start}", text)]
            filename_to_snippets[filename].append((starting_point, len(snippets) - 1))
    expected_snippets = len(snippets)
    query = get_prompt(diff, snippets)
    llama = llm_helpers.LLamathonClient()
    llama.load_groq_client()
    llama.set_model(llm_helpers.SupportedModels.LLAMA3_70b)
    result = llama.get(query)
    result = result.content.split('```')
    final_code_snippets = []
    for i in range(expected_snippets):
        final_code_snippets.append(result[(i * 2) + 1])
    for filename, filename_snippets in filename_to_snippets.items():
        with open(filename, 'r') as f:
            lines = f.readlines()
        added_lines = 0
        for starting_point, i in filename_snippets:
            starting_point += added_lines
            new_code = final_code_snippets[i].split('\n')
            new_code = [f"{e}\n" for e in new_code if e]
            lines = lines[:starting_point] + new_code + lines[starting_point:]
            added_lines += len(new_code)
        with open(filename, 'w') as f:
            for line in lines:
                f.write(line)


if __name__ == "__main__":
    main()
