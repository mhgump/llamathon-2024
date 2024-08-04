import json
import os
import sys
from typing import List

from src.scripts.process_target_projects import PROJECTS
from src.scripts.target_project import TargetProjectLoader


def find_all_matches(content: str, snippet: str):
    linenumbers = []
    next_loc = content.find(snippet)
    while next_loc != -1:
        linenumber = content.count('\n', 0, next_loc)
        if len(linenumbers) > 0:
            linenumber += linenumbers[-1]
        linenumbers.append(linenumber)
        content = content[next_loc:]
        next_loc = content.find(snippet, next_loc + 1)
    return linenumbers


def match_snippet(working_directory: str,
                  project_shortname: str,
                  python_version: str,
                  snippet: str,
                  snippet_extension: str):
    with open(PROJECTS, 'r') as f:
        projects = json.load(f)
    project_info = None
    for project in projects:
        if project["project_shortname"] == project_shortname and project["python_version"] == python_version:
            project_info = project
            break
    if project_info is None:
        print(f"Project {project_shortname} with version {python_version} not found.")
        return
    loader = TargetProjectLoader(working_directory)
    directory = loader.clone(
        project_shortname=project_shortname,
        project_name=project_info["project_name"],
        commit_id=project_info["commit_id"],
    )
    extension_matched_files = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(snippet_extension):
                extension_matched_files += [os.path.join(root, filename)]
    matched_files = []
    for filename in extension_matched_files:
        clean_filename = filename.replace(directory, '').lstrip('/')
        with open(filename, 'r') as f:
            for linenumber in find_all_matches(f.read(), snippet):
                matched_files.append((filename, clean_filename, linenumber))
    return matched_files


if __name__ == '__main__':
    _working_directory = sys.argv[1]
    _project_shortname = sys.argv[2]
    _python_version = sys.argv[3]
    _snippet = sys.argv[4]
    _snippet_extension = sys.argv[5]
    match_snippet(_working_directory, _project_shortname, _python_version, _snippet, _snippet_extension)
