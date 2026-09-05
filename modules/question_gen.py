# modules/question_gen.py
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_questions(resume_text, round_type="technical", num_questions=3):
    """
    Generate interview questions based on round type.
    
    Args:
        resume_text: Extracted text from resume
        round_type: "aptitude", "technical", "coding", or "hr"
        num_questions: Number of questions to generate
    
    Returns:
        String with numbered questions, one per line
    """
    

    round_prompts = {
        "aptitude": f"""
        Generate {num_questions} MATHEMATICAL APTITUDE questions covering real quantitative reasoning topics.
        
        Focus on these types of questions:
        - Number series and patterns (e.g., 2, 4, 8, 16, ?)
        - Simple percentage calculations (e.g., 20% of 500)
        - Ratio and proportion problems
        - Simple interest and profit-loss calculations
        - Speed, distance, and time problems
        - Basic probability questions
        - Number system basics (odd, even, prime numbers)
        
        Keep questions BEGINNER to INTERMEDIATE level - simple enough for freshers but test basic math skills.
        Include numerical values or simple word problems.
        Do NOT include logic puzzles or reasoning about hypothetical scenarios.
        
        Ignore the resume content for this round.
        Return only the questions as a numbered list (no solutions or explanations).
        """,
        "technical": f"""
        Based on this resume, generate {num_questions} BASIC TECHNICAL questions.
        Focus on fundamental concepts and simple technology questions.
        Ask easy questions about their technical background - avoid advanced topics.
        Questions should be beginner-friendly and straightforward.
        
        Resume:
        {resume_text}
        
        Return only the questions as a numbered list (no explanations).
        """,
        "coding": f"""
        Please generate {num_questions} BEGINNER-LEVEL programming challenges for a coding round.
        
        Focus on VERY BASIC and EASY topics only:
        - Simple arithmetic operations
        - Using conditional statements (if/else)
        - Basic loops (for, while)
        - Simple array/list operations
        - Basic function definitions
        
        Example difficulty level:
        - "Write a program to check if a number is odd or even"
        - "Write a program to find the sum of first 10 numbers"
        - "Write a program to print multiplication table of 5"
        - "Write a program to find the maximum of 3 numbers"
        - "Write a program to reverse a simple number"
        
        IMPORTANT: Ask candidates to specify which programming language they will use (Python, JavaScript, Java, C++, etc.)
        Keep problems SHORT and SIMPLE - no complex algorithms, data structures, or advanced concepts.
        
        Return only the coding problems as a numbered list (no solutions or explanations).
        """,
        "hr": f"""
        Based on this resume, generate {num_questions} SIMPLE HR/BEHAVIORAL questions.
        Focus on personality, communication, and basic teamwork skills.
        Ask easy, straightforward questions suitable for beginners.
        Avoid complex scenarios - keep questions simple and direct.
        
        Resume:
        {resume_text}
        
        Return only the questions as a numbered list (no explanations).
        """
    }

    prompt = round_prompts.get(round_type, round_prompts["technical"])
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content