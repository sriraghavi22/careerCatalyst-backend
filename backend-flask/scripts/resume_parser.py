import sys
import json
import pdfplumber

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    with pdfplumber.open(file_path) as pdf:
        text = ''.join([page.extract_text() for page in pdf.pages if page.extract_text()])
    return text.strip()

if __name__ == "__main__":
    file_path = sys.argv[1]  # Get file path from Node.js call

    resume_text = extract_text_from_pdf(file_path)

    result = {
        "resume_text": resume_text
    }

    print(json.dumps(result))  # Output resume text as JSON