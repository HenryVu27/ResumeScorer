# import libraries
from openai import OpenAI
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import yaml
from PyPDF2 import PdfReader 
import json
import re

def read_pdf(path):
    reader = PdfReader(path) 
    data = ""
    for page_no in range(len(reader.pages)):
        page = reader.pages[page_no] 
        data += page.extract_text()
    return data 

def extract_json(content):
    try:
        # find first and last curly braces
        match = re.search(r'(\{.*\})', content, re.DOTALL)
        if match:
            json_str = match.group(1)
            return json.loads(json_str)  # parse the extracted JSON string
        else:
            raise ValueError("No valid JSON found in the input.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")

def ats_reader(resume_data, api_key):

    prompt = '''
    Please read the following resume text and generate a structured JSON response with the exact keys listed below. 
    Make sure each field is captured even if it is missing or unknown in the text. Use an empty string or null if the information is not provided.
    JSON Schema (strictly follow this):
    {
    "full_name": "",
    "contact_information": {
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": ""
    },
    "employment_details": [
        {
        "position": "",
        "organization": "",
        "location": "",
        "start_date": "",
        "end_date": "",
        "responsibilities": []
        }
    ],
    "education": [
        {
        "school": "",
        "degree": "",
        "location": "",
        "start_date": "",
        "end_date": "",
        "description": []
        }
    ],
    "projects": [
        {
        "name": "",
        "technologies": [],
        "start_date": "",
        "end_date": "",

        "description": []
        }
    ],
    "technical_skills": {
        "languages": [],
        "frameworks_and_libraries": [],
        "developer_tools": []
    },
    "certifications": []
    }
    Important Notes:
    Always include every key in the JSON schema, even if some data is not available.
    Use “start_date” and “end_date” instead of “duration” or “date.”
    Make sure to collect all responsibilities under “responsibilities,” and all project details under “description.”
    If a field is not present in the text, leave it as an empty string or an empty array.
    Strictly maintain the JSON format with correct nesting and data types.
    Now, provide the structured JSON as described.

    '''

    openai_client = OpenAI(
        api_key = api_key
    )    

    messages=[
        {"role": "system", 
        "content": prompt}
        ]
    
    user_content = resume_data
    
    messages.append({"role": "user", "content": user_content})

    response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.0,
                max_tokens=1500)
    
    data = response.choices[0].message.content
    return data

def get_data_from_json(data):
    name = data['full_name']
    contact = data['contact_information']
    education = data['education']
    experience = data['employment_details']
    projects = data['projects']
    technical_skills = data['technical_skills']
    certifications = data['certifications']
    skills = set()
    for skill in technical_skills.values():
        for s in skill:
            s = s.strip()
            skills.add(s)
    for project in projects:
        for s in project['technologies']:
            s = s.strip()
            skills.add(s)
    skills = list(skills)

    return name, contact, education, experience, projects, skills, certifications

if __name__ == "__main__":
    # Parse resume using GPT-4o
    # Comment to avoid calling API
    # api_key = None
    # CONFIG_PATH = r"config.yaml"
    # with open(CONFIG_PATH) as file:
    #     data = yaml.load(file, Loader=yaml.FullLoader)
    #     api_key = data['OPENAI_API_KEY']
    # resume_path = "./Resume.pdf"
    # resume_data = read_pdf(resume_path)
    # with open('output.txt', 'w') as f:
    #     print(str(ats_reader(resume_data, api_key)), file = f)

    with open('./output.txt', 'r') as f:
        data = f.read()
    parsed_json = extract_json(data)
    name, contact, education, experience, projects, skills, certifications = get_data_from_json(parsed_json)
    print(f'Name: {name}')
    print(f'Contact: {contact}')
    print(f'Education: {education}')
    print(f'Experience: {experience}')
    print(f'Projects: {projects}')
    print(f'Skills: {skills}')
    print(f'Certifications: {certifications}')

