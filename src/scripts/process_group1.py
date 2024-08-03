import argparse
import re 
import pdb # just for testing.
import json
import os

from typing import List
from github import Github
from llama import part1_prompts
from llama import llm_helpers

current_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = f"{current_dir}/output"

# Don't need auth because we're only looking at public projects. 
github_token = open("GITHUB_TOKEN", "r").read().strip()
github = None
if (not github_token):
    print("Missing github token. Will proceed without auth, but may run into rate limits.")
    github = Github()
else:
    github = Github(github_token)

llama = llm_helpers.LLamathonClient()
llama.load_groq_client()
llama.set_model(llm_helpers.SupportedModels.LLAMA3_70b)

"""Process all given repos and write the output to OUTPUT_DIR."""
def process(input_repos: List[str]): 
    info = []
    for repo_name in input_repos:
        repo_name = repo_name.strip()
        repo = github.get_repo(repo_name)
        repo_info = extract_repo_info(repo); 
        info.append(repo_info)
       
    file_path = f'{OUTPUT_DIR}/group1.json'
    with open(file_path, 'w') as file:
        json.dump(info, file, indent=4)
    return

'''
todo exclud ebig commits and files 

tag function 1. 
* Go through all dependencies right now use that to decide which diff strings to keep 

2. 
Go through all the python code and pull out functions 

^ jk dont need to do, we'll use llama 

mb before we even look in the repo, do a github search of github strings for the python regex 


'''

"""Extract information per repo."""
def extract_repo_info(repo): 
    commits = [repo.get_commit("ea18bb2"), repo.get_commit("42f3203")]# repo.get_commits()
    repo_info = {
        "repoName": repo.name, 
        "commits": [], 
    }
        
    # Collect commit diffs that mention a specific python version
    for commit in commits:
        commit_info = {
            "sha": commit.sha, 
        }
        print(commit)
        # To start, just look deeper into commits that mention an upgrade in the commit message. 
        versions = contains_python_version(commit.commit.message)        
        if not len(versions): 
            continue
        
        commit_info["versions"] = list(versions)
        commit_info["fileDiffs"] = check_commit_diff(repo, commit)
        repo_info["commits"].append(commit_info)
    return repo_info

def check_commit_diff(repo, commit):
    parent_commit = commit.parents[0] if commit.parents else None
    if (not parent_commit):
        return None

    comparison = repo.compare(parent_commit.sha, commit.sha)
    fileDiffs = []
    for file in comparison.files:
        if not file.filename.endswith('.py'): # i think this is wrong, need at least requirements.txt diff right 
            continue 
        
        query = part1_prompts.get_prompt(file.patch)
        print(query)
        result = llama.get(query)        
        fileDiffs.append({
            "filename": file.filename, 
            "tags": result.content.split('\n'), 
        })
    return fileDiffs

"""Parse out only the changed lines from a commit diff."""
# def extract_changed_lines(patch: str):
#     changed_lines = {'added': [], 'removed': []}
    
#     # Split the patch into lines
#     lines = patch.splitlines()
    
#     for line in lines:
#         if line.startswith('+') and not line.startswith('+++'):
#             changed_lines['added'].append(line[1:].strip())
#         elif line.startswith('-') and not line.startswith('---'):
#             changed_lines['removed'].append(line[1:].strip())
    
#     return changed_lines

def contains_python_version(text): 
    # Matches python followed by something semver like, case-insensitive. 
    pattern = re.compile(r'\bPython\s+(\d+\.\d+(?:\.\d+)?)\b', re.IGNORECASE)
    matches = pattern.findall(text)
    return set(matches)

def main():
    parser = argparse.ArgumentParser(description="Process group 1 type repos")
    parser.add_argument('--input_repos', nargs='+', required=True, help='List of GitHub repositories in the format owner/repo delimited by spaces.')

    args = parser.parse_args()
    process(args.input_repos)

if __name__ == "__main__":
    main()