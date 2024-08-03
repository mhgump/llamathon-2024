from github import Github
import json
import os
import sys
from typing import Dict, List, Tuple

from src.scripts.target_project import TargetProject, TargetProjectLoader


def unpack_project_info(project_info):
    commit_info_list = []
    for project_shortname in project_info:
        project_name = project_info[project_shortname]["project_name"]
        for commit_info_item in project_info[project_shortname]["commits"]:
            commit_info_list.append((
                project_shortname,
                project_name,
                commit_info_item['python_version'],
                commit_info_item['commit_id']
            ))
    return commit_info_list


def load_target_projects(projects: List[Tuple[str, str, str, str]],
                         working_directory: str) -> List[TargetProject]:
    """

    :param projects: project_uri, commit_id
    :param working_directory:
    :return:
    """
    target_projects = []
    loader = TargetProjectLoader(working_directory)
    for project_shortname, project_name, _, commit_id in projects:
        target_projects.append(loader.load(
            project_shortname=project_shortname,
            project_name=project_name,
            commit_id=commit_id,
        ))
    return target_projects


def main(source_data_directory: str, target_directory: str, python_version: str):
    """Generate commits for a target project given source commits that may be applicable.

    :param source_data_directory: Contains commit data in json files.
    :param target_directory: Target project directory
    :param python_version: Python version to filter on
    :return:
    """
    source_data = []
    for file in os.listdir(source_data_directory):
        if not file.endswith(".json"):
            continue
        _this_source_data = []
        with open(os.path.join(source_data_directory, file), "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                source_data += _this_source_data
            elif isinstance(data, dict):
                _this_source_data.append(data)
        for item in _this_source_data:
            if not isinstance(item, dict):
                continue
            if "python_version" not in item or item["python_version"] != python_version:
                continue
            source_data.append(item)

    segments = []  # TODO: Get these from source_data jsons
    dependencies = []  # TODO: Get these from source_data jsons


if __name__ == "__main__":
    _working_directory = sys.argv[1]
    _project_info = json.load(open("data/targeted_projects.json", 'r'))
    _project_info = unpack_project_info(_project_info)
    _projects = load_target_projects(_project_info, _working_directory)

