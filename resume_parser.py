import numpy as np
from pyresparser import ResumeParser
import spacy 

def ResumeParse():
    return
if __name__ == "__main__":
    nlp = spacy.load("en_core_web_sm")

    resume_path = './Resume.pdf'
    data = ResumeParser(resume_path).get_extracted_data()
    print(data)
    