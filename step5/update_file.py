import os
from groq import Groq
from dotenv import load_dotenv
import re
import json
import difflib
import argparse

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

def update_requirements(client, commits_json, current_file_content, model):
    prompt = f"""
    You are an expert in updating Python code to make it compatible with new dependency versions.
    
    Here is the JSON of commits that detail changes made for upgrading a project:
    {json.dumps(commits_json, indent=2)}

    Below is the content of a Python file from the target project that needs to be updated:
    ```
    {current_file_content}
    ```

    Your task is to apply the changes from the commits to the target Python file. 
    Follow the same pattern as in the commits and apply it accordingly to the Python file as needed.
    Ensure that you:
    - Identify and update dependency versions.
    - Make necessary usage changes to the code.
    - Adjust any hard-coded version numbers.

    Provide only the updated content of the Python file without any additional explanations.
    """

    return chat_with_groq(client, prompt, model, None)


def extract_code_block(text):
    match = re.search(r'```\n([\s\S]*?)\n```', text)
    if match:
        return match.group(1).strip()
    return text.strip()  # If no code block is found, return the stripped text

def create_patch_file(original_content, updated_content, file_to_update):
    original_lines = original_content.splitlines(keepends=True)
    updated_lines = updated_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(original_lines, updated_lines, fromfile=file_to_update, tofile=file_to_update)
    
    patch_file_name = f'{file_to_update}.patch'
    with open(patch_file_name, 'w') as f:
        f.writelines(diff)
    
    return patch_file_name

def apply_patch(patch_file_name, file_to_update):
    with open(patch_file_name, 'r') as patch_file:
        patch_content = patch_file.read()
    
    # Apply the patch using the patch command if available, otherwise manually apply
    try:
        os.system(f'patch {file_to_update} < {patch_file_name}')
    except:
        print("Applying patch manually")
        with open(file_to_update, 'r') as f:
            original_content = f.read()
        
        updated_content = original_content
        for line in patch_content.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                updated_content += line[1:] + '\n'
            elif line.startswith('-') and not line.startswith('---'):
                updated_content = updated_content.replace(line[1:] + '\n', '')
        
        with open(file_to_update, 'w') as f:
            f.write(updated_content)
    
    print("Patch applied successfully")

def main(file_to_update, json_file):
    # Use the Llama3 70b model
    model = "llama3-70b-8192"

    # Get the Groq API key and create a Groq client
    load_dotenv()
    groq_api_key = os.getenv('GROQ_API_KEY')
    client = Groq(api_key=groq_api_key)

    print("Welcome to the Requirements Updater!")

    # Load the commits JSON
    with open(json_file, 'r') as file:
        commits_json = json.load(file)

    # Load the file
    with open(file_to_update, 'r') as file:
        current_file_content = file.read()

    # Update the file
    updated_content = update_requirements(client, commits_json, current_file_content, model)

    # Extract only the content within the code block
    extracted_content = extract_code_block(updated_content)

    # Create patch file
    patch_file_name = create_patch_file(current_file_content, extracted_content, file_to_update)

    print(f"\nPatch file '{patch_file_name}' has been created.")

    # Apply the patch
    apply_patch(patch_file_name, file_to_update)

    # Clean up
    os.remove(patch_file_name)
    print("\nPatch file has been removed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update Python file based on JSON commit changes.')
    parser.add_argument('file_to_update', type=str, help='The Python file to be updated')
    parser.add_argument('json_file', type=str, help='The JSON file containing commit changes')
    args = parser.parse_args()
    
    main(args.file_to_update, args.json_file)
