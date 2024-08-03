"""Prepare a list of projects for processing.

For every project/commit:
- Get directory structure of python files
- Get all imported functionality and the lines where they are used
- Get all dependencies and their versions.
"""
from dataclasses import dataclass
from git.repo import Repo
from github import Github
from github import Auth
import os
from typing import Dict, List, Optional, Tuple

from src.scripts.helpers import detected_requirements_to_str, find_requirements


@dataclass
class TargetProject:
    project_name: str
    git_uri: str
    commit: str
    targeted_files: List[str]
    callsites: List[Tuple[str, str, int]]
    dependencies: List[Tuple[str, str]]

    def to_json(self):
        return {
            "project_name": self.project_name,
            "git_uri": self.git_uri,
            "commit": self.commit,
            "targeted_files": self.targeted_files,
            "callsites": [[e[0], e[1], e[2]] for e in self.callsites],
            "dependencies": [[e[0], e[1]] for e in self.dependencies],
        }

    def string_match_search(self, segments: List[str]) -> List[Tuple[int, str, int]]:
        """Find all files in a directory that contain any of the provided segments.

        :param segments:
        :return: List of tuples containing segment index, file name, and line number.
        """


class TargetProjectLoader:

    def __init__(self, working_directory: str):
        self._working_directory = working_directory
        self._project_name_to_directory: Dict[str, str] = {}
        token = None
        if "GITHUB_TOKEN" in os.environ:
            token = os.environ["GITHUB_TOKEN"]
        if os.path.exists("GITHUB_TOKEN"):
            token = open("GITHUB_TOKEN", 'r').read().strip()
        if token is not None:
            self._github_client = Github(auth=Auth.Token(token))
        else:
            print("Loading Github client without authentication.")
            self._github_client = Github()

    def clone(self,
              project_shortname: str,
              project_name: str,
              commit_id: str) -> str:
        git_uri = self._github_client.get_repo(project_name).git_url.replace("git://", "https://")
        if project_shortname in self._project_name_to_directory:
            directory = self._project_name_to_directory[project_shortname]
        else:
            directory = os.path.join(self._working_directory, project_shortname)
        if os.path.exists(directory):
            repo = Repo(directory)
        else:
            print(f"Cloning {git_uri} to {directory}")
            repo = Repo.clone_from(git_uri, directory)
            self._project_name_to_directory[project_shortname] = directory
        if repo.commit != commit_id:
            print(f"Checking out {commit_id} in {git_uri}")
            repo.git.checkout(commit_id)
        return directory

    @staticmethod
    def get_targeted_files(directory: str) -> List[str]:
        targeted_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    targeted_files.append(os.path.join(root, file))
        return targeted_files

    def load(self,
             project_shortname: str,
             project_name: str,
             commit_id: str) -> TargetProject:
        git_uri = self._github_client.get_repo(project_name).git_url
        local_directory = self.clone(project_shortname, project_name, commit_id)
        print("Finding requirements")
        dependencies = find_requirements(local_directory)
        print("Finding targeted files")
        targeted_files = self.get_targeted_files(local_directory)
        return TargetProject(
            project_name=project_shortname,
            git_uri=git_uri,
            commit=commit_id,
            dependencies=[detected_requirements_to_str(e) for e in dependencies],
            targeted_files=targeted_files,
            callsites=[],
        )
