import os
from groq import Groq
from dotenv import load_dotenv
import re
import json

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

# Print the updated requirements
print("\nUpdated requirements.txt")

# Optionally, save the updated requirements to a file
with open('updated_requirements.txt', 'w') as file:
    file.write(extracted_requirements)

print("\nUpdated requirements have been saved to 'updated_requirements.txt'")