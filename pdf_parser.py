#!/usr/bin/env python3
"""
PDF parsing functionality for extracting test questions
"""

import re
import os
from typing import List, Dict, Optional

class PDFQuestionExtractor:
    def __init__(self):
        self.question_patterns = [
            r'(\d+)\.\s*(.+)',  # 1. Question text
            r'(\d+)\)\s*(.+)',  # 1) Question text
            r'(\d+)\s*\.\s*(.+)',  # 1 . Question text
            r'([A-Z])\.\s*(.+)',  # A. Question text
        ]
        
        self.option_patterns = [
            r'([A-Z])\)\s*(.+)',  # A) Option text
            r'([A-Z])\.\s*(.+)',  # A. Option text
            r'([a-z])\)\s*(.+)',  # a) Option text
            r'([a-z])\.\s*(.+)',  # a. Option text
        ]
    
    def extract_questions_from_text(self, text: str) -> List[Dict]:
        """
        Extract questions and options from text
        """
        questions = []
        lines = text.split('\n')
        current_question = None
        current_options = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a question
            question_match = None
            for pattern in self.question_patterns:
                match = re.match(pattern, line)
                if match:
                    question_match = match
                    break
            
            if question_match:
                # Save previous question if exists
                if current_question and current_options:
                    questions.append({
                        'question': current_question,
                        'options': current_options.copy()
                    })
                
                # Start new question
                current_question = question_match.group(2)
                current_options = []
            
            # Check if this is an option
            elif current_question:
                option_match = None
                for pattern in self.option_patterns:
                    match = re.match(pattern, line)
                    if match:
                        option_match = match
                        break
                
                if option_match:
                    current_options.append({
                        'key': option_match.group(1).upper(),
                        'text': option_match.group(2)
                    })
                else:
                    # This might be continuation of question or option
                    if current_options:
                        # Add to last option
                        if current_options:
                            current_options[-1]['text'] += ' ' + line
                    else:
                        # Add to question
                        current_question += ' ' + line
        
        # Save last question
        if current_question and current_options:
            questions.append({
                'question': current_question,
                'options': current_options.copy()
            })
        
        return questions
    
    def parse_pdf_file(self, file_path: str) -> Optional[List[Dict]]:
        """
        Parse PDF file and extract questions
        """
        try:
            # Try to use PyPDF2 first
            try:
                import PyPDF2
                return self._parse_with_pypdf2(file_path)
            except ImportError:
                pass
            
            # Try pdfplumber as fallback
            try:
                import pdfplumber
                return self._parse_with_pdfplumber(file_path)
            except ImportError:
                pass
            
            # Try PyMuPDF as last resort
            try:
                import fitz  # PyMuPDF
                return self._parse_with_pymupdf(file_path)
            except ImportError:
                pass
            
            print("No PDF parsing library available. Please install PyPDF2, pdfplumber, or PyMuPDF.")
            return None
            
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return None
    
    def _parse_with_pypdf2(self, file_path: str) -> List[Dict]:
        """Parse PDF using PyPDF2"""
        import PyPDF2
        
        questions = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        return self.extract_questions_from_text(text)
    
    def _parse_with_pdfplumber(self, file_path: str) -> List[Dict]:
        """Parse PDF using pdfplumber"""
        import pdfplumber
        
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        
        return self.extract_questions_from_text(text)
    
    def _parse_with_pymupdf(self, file_path: str) -> List[Dict]:
        """Parse PDF using PyMuPDF"""
        import fitz
        
        text = ""
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text() + "\n"
        
        return self.extract_questions_from_text(text)

def test_pdf_parser():
    """Test the PDF parser with sample text"""
    extractor = PDFQuestionExtractor()
    
    sample_text = """
    1. Poytaxtimiz qaysi shahar?
    A) Toshkent
    B) Samarqand
    C) Buxoro
    D) Farg'ona
    
    2. O'zbekiston nechanchi yilda mustaqil bo'ldi?
    A) 1989
    B) 1991
    C) 1993
    D) 1995
    """
    
    questions = extractor.extract_questions_from_text(sample_text)
    
    print("Extracted Questions:")
    for i, q in enumerate(questions, 1):
        print(f"\n{i}. {q['question']}")
        for opt in q['options']:
            print(f"   {opt['key']}) {opt['text']}")

if __name__ == "__main__":
    test_pdf_parser()
