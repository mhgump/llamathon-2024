import os
from groq import Groq
from dotenv import load_dotenv
import re
import json
import difflib

def chat_with_groq(client, prompt, model, response_format):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format=response_format
    )
    return completion.choices[0].message.content

def update_requirements(client, commits_json, current_requirements, model):
    prompt = f"""
    Given the following JSON of commits and the current requirements.txt file:

    Commits:
    {json.dumps(commits_json, indent=2)}

    Current requirements.txt:
    {current_requirements}

    Please update the requirements.txt file to reflect the changes in the commits. 
    Provide only the updated content of the requirements.txt file, without any additional explanations.
    """

    return chat_with_groq(client, prompt, model, None)

def extract_code_block(text):
    match = re.search(r'```\n([\s\S]*?)\n```', text)
    if match:
        return match.group(1).strip()
    return text.strip()  # If no code block is found, return the stripped text

def create_patch_file(original_content, updated_content):
    original_lines = original_content.splitlines(keepends=True)
    updated_lines = updated_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(original_lines, updated_lines, fromfile='requirements.txt', tofile='requirements.txt')
    
    with open('requirements.patch', 'w') as f:
        f.writelines(diff)

def apply_patch():
    with open('requirements.patch', 'r') as patch_file:
        patch_content = patch_file.read()
    
    # Apply the patch manually
    with open('requirements.txt', 'r') as f:
        original_content = f.read()
    
    updated_content = original_content
    for line in patch_content.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            updated_content += line[1:] + '\n'
        elif line.startswith('-') and not line.startswith('---'):
            updated_content = updated_content.replace(line[1:] + '\n', '')
    
    with open('requirements.txt', 'w') as f:
        f.write(updated_content)
    
    print("Patch applied successfully")

# Use the Llama3 70b model
model = "llama3-70b-8192"

# Get the Groq API key and create a Groq client
load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key = groq_api_key)

print("Welcome to the Requirements Updater!")

# Load the commits JSON
with open('sample.json', 'r') as file:
    commits_json = json.load(file)

# Load the current requirements.txt
with open('requirements.txt', 'r') as file:
    current_requirements = file.read()

# Update the requirements
updated_requirements = update_requirements(client, commits_json, current_requirements, model)

# Extract only the content within the code block
extracted_requirements = extract_code_block(updated_requirements)

# Create patch file
create_patch_file(current_requirements, extracted_requirements)

print("\nPatch file 'requirements.patch' has been created.")

# Apply the patch
apply_patch()

# Clean up
os.remove('requirements.patch')
print("\nPatch file has been removed.")