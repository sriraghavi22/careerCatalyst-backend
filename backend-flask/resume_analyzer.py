# Install required packages
# !pip install pdfplumber pdf2image pytesseract python-dotenv google-generativeai PyPDF2
# Note: Uncomment and run this line manually in your environment if needed

# Import libraries
import os
from dotenv import load_dotenv
import google.generativeai as genai
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import tempfile
import PyPDF2
import re

class AIResumeAnalyzer:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Configure Google Gemini AI
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyDIANYygPSw0Ob6y_MoMOlgm6R-zBwg--8")
        
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
        else:
            raise ValueError("Google API key is not configured. Please set GOOGLE_API_KEY in your .env file.")

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from PDF using pdfplumber and OCR if needed"""
        text = ""
        
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_file.read())  # Assumes pdf_file is a file-like object from Flask request
            temp_path = temp_file.name
        
        try:
            # Try direct text extraction with pdfplumber
            try:
                with pdfplumber.open(temp_path) as pdf:
                    for page in pdf.pages:
                        try:
                            import warnings
                            with warnings.catch_warnings():
                                warnings.filterwarnings("ignore", message=".*PDFColorSpace.*")
                                warnings.filterwarnings("ignore", message=".*Cannot convert.*")
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
                os.unlink(temp_path)  # Clean up the temp file
                return text.strip()
            
            # Try PyPDF2 as a fallback
            print("Trying PyPDF2 extraction method...")
            try:
                pdf_text = ""
                with open(temp_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            pdf_text += page_text + "\n"
                
                if pdf_text.strip():
                    os.unlink(temp_path)  # Clean up the temp file
                    return pdf_text.strip()
            except Exception as e:
                print(f"PyPDF2 extraction failed: {e}")
            
            # If we got here, both extraction methods failed
            print("Standard text extraction methods failed. Your PDF might be image-based or scanned.")
            
            # Try OCR as a last resort
            try:
                print("Attempting OCR for image-based PDF. This may take a moment...")
                images = convert_from_path(temp_path)
                ocr_text = ""
                for i, image in enumerate(images):
                    print(f"Processing page {i+1} with OCR...")
                    page_text = pytesseract.image_to_string(image)
                    ocr_text += page_text + "\n"
                
                if ocr_text.strip():
                    os.unlink(temp_path)  # Clean up the temp file
                    return ocr_text.strip()
                else:
                    print("OCR extraction yielded no text. Please check if the PDF contains actual text content.")
            except Exception as e:
                print(f"OCR processing failed: {e}")
                print("Ensure Tesseract OCR and Poppler are installed correctly.")
        
        except Exception as e:
            print(f"PDF processing failed: {e}")
        
        # Clean up the temp file
        try:
            os.unlink(temp_path)
        except:
            pass
        
        print("All text extraction methods failed. Please try a different PDF or manually extract the text.")
        return ""

    def analyze_resume_with_gemini(self, resume_text, job_description=None, job_role=None):
        """Analyze resume using Google Gemini AI"""
        if not resume_text:
            return {"error": "Resume text is required for analysis."}
        
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            base_prompt = f"""
            You are an expert resume analyst with deep knowledge of industry standards, job requirements, and hiring practices across various fields. Your task is to provide a comprehensive, detailed analysis of the resume provided.
            
            Please structure your response in the following format:
            
            ## Overall Assessment
            [Provide a detailed assessment of the resume's overall quality, effectiveness, and alignment with industry standards. Include specific observations about formatting, content organization, and general impression. Be thorough and specific.]
            
            ## Professional Profile Analysis
            [Analyze the candidate's professional profile, experience trajectory, and career narrative. Discuss how well their story comes across and whether their career progression makes sense for their apparent goals.]
            
            ## Skills Analysis
            - **Current Skills**: [List ALL skills the candidate demonstrates in their resume, categorized by type (technical, soft, domain-specific, etc.). Be comprehensive.]
            - **Skill Proficiency**: [Assess the apparent level of expertise in key skills based on how they're presented in the resume]
            - **Missing Skills**: [List important skills that would improve the resume for their target role. Be specific and explain why each skill matters.]
            
            ## Experience Analysis
            [Provide detailed feedback on how well the candidate has presented their experience. Analyze the use of action verbs, quantifiable achievements, and relevance to their target role. Suggest specific improvements.]
            
            ## Education Analysis
            [Analyze the education section, including relevance of degrees, certifications, and any missing educational elements that would strengthen their profile.]
            
            ## Key Strengths
            [List 5-7 specific strengths of the resume with detailed explanations of why these are effective]
            
            ## Areas for Improvement
            [List 5-7 specific areas where the resume could be improved with detailed, actionable recommendations]
            
            ## ATS Optimization Assessment
            [Analyze how well the resume is optimized for Applicant Tracking Systems. Provide a specific ATS score from 0-100, with 100 being perfectly optimized. Use this format: "ATS Score: XX/100". Then suggest specific keywords and formatting changes to improve ATS performance.]
            
            ## Recommended Courses/Certifications
            [Suggest 5-7 specific courses or certifications that would enhance the candidate's profile, with a brief explanation of why each would be valuable]
            
            ## Resume Score
            [Provide a score from 0-100 based on the overall quality of the resume. Use this format exactly: "Resume Score: XX/100" where XX is the numerical score. Be consistent with your assessment - a resume with significant issues should score below 60, an average resume 60-75, a good resume 75-85, and an excellent resume 85-100.]
            
            Resume:
            {resume_text}
            """
            
            if job_role:
                base_prompt += f"""
                
                The candidate is targeting a role as: {job_role}
                
                ## Role Alignment Analysis
                [Analyze how well the resume aligns with the target role of {job_role}. Provide specific recommendations to better align the resume with this role.]
                """
            
            if job_description:
                base_prompt += f"""
                
                Additionally, compare this resume to the following job description:
                
                Job Description:
                {job_description}
                
                ## Job Match Analysis
                [Provide a detailed analysis of how well the resume matches the job description, with a match percentage and specific areas of alignment and misalignment]
                
                ## Key Job Requirements Not Met
                [List specific requirements from the job description that are not addressed in the resume, with recommendations on how to address each gap]
                """
            
            response = model.generate_content(base_prompt)
            analysis = response.text.strip()
            
            # Extract resume score if present
            resume_score = self._extract_score_from_text(analysis)
            
            # Extract ATS score if present
            ats_score = self._extract_ats_score_from_text(analysis)
            
            return {
                "analysis": analysis,
                "resume_score": resume_score,
                "ats_score": ats_score
            }
        
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _extract_score_from_text(self, analysis_text):
        """Extract the resume score from the analysis text"""
        try:
            if "## Resume Score" in analysis_text:
                score_section = analysis_text.split("## Resume Score")[1].strip()
                score_match = re.search(r'Resume Score:\s*(\d{1,3})/100', score_section)
                if score_match:
                    score = int(score_match.group(1))
                    return max(0, min(score, 100))
                
                score_match = re.search(r'\b(\d{1,3})\b', score_section)
                if score_match:
                    score = int(score_match.group(1))
                    return max(0, min(score, 100))
            
            score_match = re.search(r'Resume Score:\s*(\d{1,3})/100', analysis_text)
            if score_match:
                score = int(score_match.group(1))
                return max(0, min(score, 100))
                
            return 0
        except Exception as e:
            print(f"Error extracting score: {str(e)}")
            return 0
            
    def _extract_ats_score_from_text(self, analysis_text):
        """Extract the ATS score from the analysis text"""
        try:
            if "## ATS Optimization Assessment" in analysis_text:
                ats_section = analysis_text.split("## ATS Optimization Assessment")[1].split("##")[0].strip()
                score_match = re.search(r'ATS Score:\s*(\d{1,3})/100', ats_section)
                if score_match:
                    score = int(score_match.group(1))
                    return max(0, min(score, 100))
            return 0
        except Exception as e:
            print(f"Error extracting ATS score: {str(e)}")
            return 0

if __name__ == "__main__":
    # This block is for testing purposes only (e.g., in Colab or locally)
    analyzer = AIResumeAnalyzer()
    # Add test code here if needed, but it won't use files.upload() in a server context
    pass