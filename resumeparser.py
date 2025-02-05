# import libraries
from openai import OpenAI
import yaml
from pypdf import PdfReader 
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
            return json.loads(json_str)  # Parse the extracted JSON string
        else:
            raise ValueError("No valid JSON found in the input.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")

def ats_reader(resume_data, api_key):

    prompt = '''
    You are an AI bot designed to act as a professional for parsing resumes. You are given with resume and your job is to extract the following information from the resume:
    1. full name
    2. contact information (email, phone, github, linkedin, etc.)
    3. employment details
    4. personal project
    5. technical skills
    6. certifications
    Give the extracted information in json format only
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

if __name__ == "__main__":
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
    for key, val in parsed_json.items():
        print(f'{key}: {val}')
