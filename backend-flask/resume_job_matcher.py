import os
from dotenv import load_dotenv
import google.generativeai as genai
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import tempfile
import PyPDF2
import re

class ResumeJobMatcher:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Configure Google Gemini AI
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyDIANYygPSw0Ob6y_MoMOlgm6R-zBwg--8")
        
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
        else:
            raise ValueError("Google API key is not configured. Please set GOOGLE_API_KEY in your .env file.")

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using pdfplumber and OCR if needed"""
        text = ""
        
        try:
            # Try direct text extraction with pdfplumber
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        try:
                            import warnings
                            with warnings.catch_warnings():
                                warnings.filterWarnings("ignore", message=".*PDFColorSpace.*")
                                warnings.filterWarnings("ignore", message=".*Cannot convert.*")
                                page_text = page.extract_text()
                                if page_text:
                                    text += page_text + "\n"
                        except Exception as e:
                            if "PDFColorSpace" not in str(e) and "Cannot convert" not in str(e):
                                print(f"Error extracting text from page with pdfplumber: {e}")
            except Exception as e:
                print(f"pdfplumber extraction failed: {e}")
            
            # If pdfplumber extraction worked, return the text
            if text.strip():
                return text.strip()
            
            # Try PyPDF2 as a fallback
            print("Trying PyPDF2 extraction method...")
            try:
                pdf_text = ""
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            pdf_text += page_text + "\n"
                
                if pdf_text.strip():
                    return pdf_text.strip()
            except Exception as e:
                print(f"PyPDF2 extraction failed: {e}")
            
            # Try OCR as a last resort
            try:
                print("Attempting OCR for image-based PDF. This may take a moment...")
                images = convert_from_path(pdf_path)
                ocr_text = ""
                for i, image in enumerate(images):
                    print(f"Processing page {i+1} with OCR...")
                    page_text = pytesseract.image_to_string(image)
                    ocr_text += page_text + "\n"
                
                if ocr_text.strip():
                    return ocr_text.strip()
                else:
                    print("OCR extraction yielded no text. Please check if the PDF contains actual text content.")
            except Exception as e:
                print(f"OCR processing failed: {e}")
                print("Ensure Tesseract OCR and Poppler are installed correctly.")
        
        except Exception as e:
            print(f"PDF processing failed: {e}")
        
        print("All text extraction methods failed. Please try a different PDF or manually extract the text.")
        return ""

    def match_resume_to_job(self, resume_path, job_description, job_role=None):
        """Generate a match score (0–100) for a resume and job description using Google Gemini AI"""
        # Extract resume text
        resume_text = self.extract_text_from_pdf(resume_path)
        if not resume_text:
            return {"error": "Failed to extract text from resume"}
        
        if not job_description:
            return {"error": "Job description is required for matching"}
        
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            You are an expert in resume-job matching with deep knowledge of hiring practices and job requirements across various industries. Your task is to evaluate how well the provided resume matches the given job description and provide only a numerical match score from 0 to 100. Do not include any analysis, explanations, or additional details. A score below 60 indicates a poor match, 60–75 is average, 75–85 is good, and 85–100 is excellent.

            Return the response in this exact format:
            Match Score: XX/100

            Resume:
            {resume_text}

            Job Description:
            {job_description}
            """
            
            if job_role:
                prompt += f"""
                The candidate is targeting a role as: {job_role}
                Consider the specific expectations and skills associated with this role when calculating the score.
                """

            response = model.generate_content(prompt)
            analysis = response.text.strip()
            
            # Extract match score
            match_score = self._extract_score_from_text(analysis)
            
            return {
                "match_score": match_score
            }
        
        except Exception as e:
            return {"error": f"Matching failed: {str(e)}"}
    
    def _extract_score_from_text(self, analysis_text):
        """Extract the match score from the analysis text"""
        try:
            score_match = re.search(r'Match Score:\s*(\d{1,3})/100', analysis_text)
            if score_match:
                score = int(score_match.group(1))
                return max(0, min(score, 100))
                
            score_match = re.search(r'\b(\d{1,3})\b', analysis_text)
            if score_match:
                score = int(score_match.group(1))
                return max(0, min(score, 100))
            
            return 0
        except Exception as e:
            print(f"Error extracting score: {str(e)}")
            return 0

if __name__ == "__main__":
    # For testing purposes
    matcher = ResumeJobMatcher()
    # Add test code here if needed
    pass