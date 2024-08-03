import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = f"{current_dir}/output"

good_commits = None
with open(f"{OUTPUT_DIR}/good_commits.json", 'r') as file:
    good_commits = json.load(file)
    
snippets = None
with open(f"{OUTPUT_DIR}/group1.json", 'r') as file:
    snippets = json.load(file)
    
output = {}
for repo, commit_shas in good_commits.items(): 
    output[repo] = []
    repo_name = repo.split('/')[1].strip()
    
    repo_snippets = None
    for r_snippets in snippets:
        if r_snippets["repoName"] == repo_name:
            repo_snippets = r_snippets
            break
    if repo_snippets is None:
        print(f"i couldnt find repo {repo_name}")
        raise Exception(":(")
        
    # per good commit sha
    for sha in commit_shas: 
        # find the relevant commit snippets by sha 
        commit = None
        for c in repo_snippets["commits"]: 
            if c["sha"] == sha: 
                commit = c
                break
        if c is None: 
            print(f"i couldnt find commit sha {sha}")
            raise Exception(":(")

        # With the commit, concat all the file diffs but tag them with the extension
        tags = [] 
        for file in c["fileDiffs"]:
            extension = file["filename"].split(".")[-1]
            for t in file["tags"]:
                tags.append(f"{t} delimiter {extension}")
                
        tags = list(set(tags))
        output[repo].append({
            "sha": sha, 
            "tags": tags, 
        })
        

file_path = f'{OUTPUT_DIR}/tagged_good_commits.json'
with open(file_path, 'w') as file:
    json.dump(output, file, indent=4)
            
