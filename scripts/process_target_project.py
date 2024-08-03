import json
import os
from typing import List, Tuple

from scripts.target_project import TargetProject, load as target_project_load


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

    result: TargetProject = target_project_load(target_directory)
    match_tuples: List[Tuple[int, str, int]] = []
    match_tuples += result.string_match_search(segments)
