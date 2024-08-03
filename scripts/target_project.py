"""Prepare a list of projects for processing.

For every project/commit:
- Get directory structure of python files
- Get all imported functionality and the lines where they are used
- Get all dependencies and their versions.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from scripts.helpers import detected_requirements_to_str, find_requirements


@dataclass
class TargetProject:
    project_name: str
    git_url: str
    commit: str
    python_files: List[str]
    imported_functionality: List[str]
    callsites: Dict[str, Tuple[str, int]]
    dependencies: Tuple[str, str]

    def to_json(self):
        return {
            "project_name": self.project_name,
            "git_url": self.git_url,
            "commit": self.commit,
            "python_files": self.python_files,
            "imported_functionality": self.imported_functionality,
            "callsites": {k: [v[0], v[1]] for k, v in self.callsites.items()},
            "dependencies": [[e[0], e[1]] for e in self.dependencies],
        }

    def string_match_search(self, segments: List[str]) -> List[Tuple[int, str, int]]:
        """Find all files in a directory that contain any of the provided segments.

        :param segments:
        :return: List of tuples containing segment index, file name, and line number.
        """


def load(git_uri: str, directory: Optional[str]=None) -> TargetProject:
    """

    :param project_directory:
    :return:
    """
    if directory is None:
        # Get directory from git_uri
        pass

    dependencies = find_requirements(directory)
    TargetProject(
        project_name = directory.strip('/').split('/')[-1],
        gir_uri=git_uri,
        dependencies=[detected_requirements_to_str(e) for e in dependencies],
