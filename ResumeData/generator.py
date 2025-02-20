from openai import OpenAI
import csv
import random
import time
import yaml

RESUMES_PER_POSITION = 1

job_titles = [
    "Data Scientist",
    "Data Analyst",
    "Machine Learning Engineer",
    "Software Engineer",
    "Frontend Developer",
    "Backend Developer",
    "DevOps Engineer",
    "Mobile Developer",
    "Cybersecurity Analyst",
    "Product Manager",
    "Full Stack Developer",
    "Cloud Architect",
    "Database Administrator",
    "Systems Analyst",
    "Business Analyst",
    "QA Engineer"
]

rating_criteria = {
    (1,2,3): "Missing most required skills, unclear structure, grammar issues, minimal relevant experience.",
    (4,5,6): "Partial match to required skills, some relevant experience, moderate clarity, minor errors.",
    (7,8):   "Good match to required skills, clear structure, well-written, some small gaps.",
    (9,10):  "Excellent match, covers key skills thoroughly, strong achievements, polished and professional."
}

def get_criteria(rating):
    # return the description for the rating
    for range, score in rating_criteria.items():
        if rating in range:
            return score
    return rating_criteria[(4,5,6)]  # fallback mechanism in case model generates outside of 1-10, should never happen logically

OUTPUT_CSV = "resume_data.csv"

prompt_template = """
You are an expert resume writer. 
Generate a realistic resume tailored for the role: {job_position}.
RATING: {rating}/10
RATING DEFINITION: {criteria}

RESUME REQUIREMENTS:
- Reflect the rating definition in terms of skills, experience, grammar/structure.
- If rating is low, include obvious shortcomings (missing skills, weaker experience, or poor formatting).
- If rating is high, demonstrate depth of experience, strong achievements, and clarity.

The resume should look realistic in structure and should generally contain the following fields: 
- Full name, contact details and relevant websites
- Summary (optional, should have 10 percent chance of being generated)
- Experience
- Education
- Project
- Skills
- Others (optinal)
"""

def generate_resume(client, job_title, rating):
    criteria_desc = get_criteria(rating)
    prompt = prompt_template.format(job_position = job_title, rating = rating, criteria = criteria_desc)
    system_message = {"role": "system", "content": "You are an expert resume writer. Follow the rating definition instructions strictly."}
    user_message = {"role": "user", "content": prompt}
    response = client.chat.completions.create(
                model="gpt-4o",
                messages = [system_message, user_message],
                temperature = 0.0,
                max_tokens = 500)
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    # Create OpenAI client
    api_key = None
    CONFIG_PATH = r"../config.yaml"
    with open(CONFIG_PATH) as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
        api_key = data['OPENAI_API_KEY']
    openai_client = OpenAI(api_key = api_key)

    with open(OUTPUT_CSV, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["job_title", "resume_text", "score"])
        
        for title in job_titles:    
            for _ in range(RESUMES_PER_POSITION):
                rating = random.randint(1, 10)
                try:
                    resume_text = generate_resume(openai_client, title, rating)
                    writer.writerow([title, resume_text, rating])
                except Exception as e:
                    print(f"Error generating resume for {title}, label {rating}: {e}")                
                time.sleep(0.5)

    print("Data generation complete!")